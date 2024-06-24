#pragma once

#include <climits>
#include <algorithm>

#include "IQ.h"
#include "ChainLink.h"

//#define SET_DELAY_ON_START
//#define RELATIVE_MOVE
//#define TRIG_LOOKUP

#ifdef RELATIVE_MOVE
//long dxmm = 0, dymm = 10000, dzmm = 0; // offset in mm
#endif // RELATIVE_MOVE


class Resample : public ChainLink{
	const long long PHASE_POWER = 30;
	const long long PHASE_RANGE = (1 << PHASE_POWER);
public:
	long radioFrequencyOut;
	long radioFrequencyIn;

	long inputRate;
	long outputRate;

	IQ currentSample;

	long long n = 0;
	long long itterNStep;
	long long bufferNStep;
	long long delayNStep = 0;
	const int subCycles = 10000;

	long unitStepPhase;
	long unitPhase;

	int power = 1;

	long long last_set_delay = 0;
	long long last_target = 0;

	long long dx = 0, dy = 0, dz = 0; // offset n per meter
#ifdef RELATIVE_MOVE
	long long dxn = 0, dyn = 0, dzn = 0; // current ofset in n
	long long dnstep = 1; // how fast to go to target
	long long dxmm = 0, dymm = 0, dzmm = 0; // offset in mm
#endif

	ChainLink* dataSource;
	ChainLink* sampleSource;
public:

	

	Resample(): currentSample(0.0f) {
		//init();
	}

	void init() {
		itterNStep = subCycles * (long long)inputRate;// *(targetFrequency / (double)radioFrequency); // might trow of updating of delay
		bufferNStep = subCycles * (long long)outputRate;

#ifdef RELATIVE_MOVE

		dnstep = bufferNStep / 3 / 10230;
#endif

		//n = 0;
		//last_set_delay = 0;
		//setDelay(0);

		unitPhase = 0;
		setDopler(0);

		sampleSource->init();
		currentSample = sampleSource->nextSample();
	}

	void setDopler(float f) {

		//std::cout << "doppler s: " << f << std::endl;

		int64_t scale = 1000;
		//std::cout << "setDopler" << std::endl;
		int64_t dopplerShift = (double)f * scale;
		int64_t targetFrequency = dopplerShift + (int64_t)radioFrequencyIn * scale;
		int64_t shift = targetFrequency - radioFrequencyOut * scale;
		double normalPhaseSampleDelta = shift / (double)outputRate;
		unitStepPhase = normalPhaseSampleDelta / scale * PHASE_RANGE;// (LONG_MAX / 2);
		//std::cout << "   doppler: " << unitStepPhase << ", " << normalPhaseSampleDelta;
		//std::cout << f << "_" << shift/(float)scale << ", phase normal step: " << normalPhaseSampleDelta << ", unit: " << unitStepPhase <<std::endl;
	}

	void setPower(int power) {
		this->power = power;
	}

	void setDxyz(float dx, float dy, float dz) { // in ms
		this->dx = calcDelayNum(dx);
		this->dy = calcDelayNum(dy);
		this->dz = calcDelayNum(dz);
	}

	void print_info() {
		//std::cout << targetFrequency << "/" << radioFrequencyOut << std::endl;
		//std::cout << std::setprecision(15) << targetFrequency / (double)radioFrequencyOut << std::endl;
		std::cout << itterNStep / (float)subCycles << " <- " << inputRate << " (" << itterNStep - inputRate * subCycles << ")" << std::endl;
		//std::cout << std::setprecision(15) << "Phase Delta: " << normalPhaseSampleDelta << " $ " << unitStepPhase << std::endl;
		std::cout << "frequency: " << radioFrequencyIn << std::endl;
		std::cout << std::endl;
	}

	uint8_t nextBit() {
		//std::cout << "offset(mm): " << dymm << ", n/m: " << dy << ", target: " << dymm*dy/1000 << ", current(n): " << dyn << std::endl;
		return dataSource->nextBit();
	}

	long long calcDelayNum(double delay_ms) {
		double delay_samples = delay_ms / 1000 * outputRate;
		long delay_whole_samples = (long)delay_samples;
		double delay_partial_samples = delay_samples - delay_whole_samples;

		long long nPerSample = ((long long)subCycles * inputRate); /*itterNStep*/

		long long whole_delay = delay_whole_samples * nPerSample;
		long long partial_delay = (long long)(delay_partial_samples * nPerSample);

		long long delay = whole_delay + partial_delay;

		//std::cout << delay << std::endl;

		return delay;
	}

	long long numToPhaseStep(long long n) {
		//long long nPerSample = ((long long)subCycles * inputRate); /*itterNStep*/
		//long long samples = n / (subCycles * inputRate);
		//double delay_ms = samples * 1000 / outputRate;


		//double delay_ms = n / (subCycles * inputRate * outputRate) * 1000;

		//double waveLength_ms = 1 / radioFrequencyOut * 1000;

		//double phase_step = delay_ms / waveLength_ms;
		//long long phase_step = n * radioFrequencyOut * PHASE_RANGE / (subCycles * inputRate * outputRate);//2^80 / ...
		long long phase_step = n * radioFrequencyOut / (subCycles * inputRate) * PHASE_RANGE / outputRate;
		//std::cout << phase_step / (double)PHASE_RANGE << std::endl;
		return phase_step;
		//return PHASE_RANGE * phase_step;
	}

	void setDelay(double delay_ms) {
#ifdef SET_DELAY_ON_START
		// n time
		long long new_delay = calcDelayNum(delay_ms);
		//std::cout << "old: " << n;
		n = n + last_set_delay - new_delay;
		last_set_delay = new_delay;
#endif
	}


	void setDelayTarget(double delay_ms, double time_till_next_update) {


		//static long long last_target = 0;

		long long new_delay = calcDelayNum(delay_ms);
		long long last_delay = this->last_set_delay;
		long long samples_inbetween = this->outputRate * time_till_next_update;
		long long delay_change = new_delay - last_delay;
		//long long delay_change = last_delay - new_delay;
		long long new_delayNStep = delay_change / samples_inbetween;
		/*if (abs(new_delayNStep - delayNStep) < 10000) {
			delayNStep = (new_delayNStep*2 + delayNStep) / 3;
		}
		else {
			delayNStep = new_delayNStep;
			std::cout << "overwrite smooth" << std::endl;
		}*/
		delayNStep = new_delayNStep;
		//std::cout << "   delayNStep: " << delayNStep << " " << new_delay << " " << last_target << " " << last_target-last_delay << std::endl;
		//std::cout << last_target - last_delay << std::endl;


		last_target = new_delay;
		//std::cout << std::setprecision(10) << delay_ms << " <> " << new_delay*1000.0 / subCycles / inputRate / outputRate << std::endl;

		// calculate doppler form delay
		//double speedup = (double)-new_delayNStep / itterNStep;
		//std::cout << "doppler d: " << speedup * this->radioFrequencyOut << std::endl;



		/*long long added_delay = new_delay - this->last_set_delay;
		long long modulationRate = this->inputRate;

		//delayNStep = int(     added_delay * itterNStep     / (bufferNStep * modulationRate / 10                   + added_delay)) # f(delay_n)
		long long test_delayNStep = (double)added_delay * itterNStep / (bufferNStep * modulationRate * time_till_next_update + added_delay);
		std::cout << delayNStep << " - " << test_delayNStep << std::endl;*/
	}

	IQ nextSample() {

#ifdef RELATIVE_MOVE
		long dxnstep = std::clamp((dx * dxmm / 1000) - dxn, -dnstep, dnstep);
		dxn += dxnstep;
		long dynstep = std::clamp((dy * dymm / 1000) - dyn, -dnstep, dnstep);
		dyn += dynstep;
		long dznstep = std::clamp((dz * dzmm / 1000) - dzn, -dnstep, dnstep);
		dzn += dznstep;
		long dxyznstep = dxnstep + dynstep + dznstep;
		n += dxyznstep;

		//if (dynstep != 0) {
		//	std::cout << "step y " << dynstep << std::endl;
		//}
#endif


		while (n >= bufferNStep) {
			n -= bufferNStep;
			currentSample = sampleSource->nextSample();
		}

		n += itterNStep;

		n -= delayNStep;
		last_set_delay += delayNStep;


		IQ sample = currentSample;

		/*double current_delay = (double)last_set_delay / subCycles / inputRate / outputRate;
		double num_lambda = current_delay * radioFrequencyIn;
		double lambda_fraction = fmod(num_lambda, 1);
		sample = sample.rotate(lambda_fraction * 2 * M_PI);*/

		/*static long long timer = 0;
		if (timer < 15000000) {
			timer++;
		}
		else {
			std::cout << num_lambda << " _ " << lambda_fraction << " _ " << lambda_fraction*2*M_PI << " / " << (unitPhase / (float)PHASE_RANGE) * 2 * M_PI << std::endl;
		}*/


		//sample = sample.rotate((unitPhase / (float)PHASE_RANGE/*(LONG_MAX / 2)*/) * 2 * M_PI);
#ifdef TRIG_LOOKUP
		sample = sample.rotate(unitPhase);
#else
		sample = sample.rotate((unitPhase / (float)PHASE_RANGE/*(LONG_MAX / 2)*/) * 2 * M_PI);
#endif

#ifdef RELATIVE_MOVE
		unitPhase += unitStepPhase+numToPhaseStep(dxyznstep);
#else
		unitPhase += unitStepPhase;
#endif
		while (unitPhase > PHASE_RANGE/*(LONG_MAX / 2)*/) {
			unitPhase -= PHASE_RANGE;// (LONG_MAX / 2);
		}
		while (unitPhase < 0) {
			unitPhase += PHASE_RANGE;// (LONG_MAX / 2);
		}
		return sample * power/100;
	}
};