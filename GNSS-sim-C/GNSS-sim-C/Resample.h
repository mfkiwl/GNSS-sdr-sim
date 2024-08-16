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

/// <summary>
/// Upsample, delay, and shift signals
/// </summary>
class Resample : public ChainLink{
	// settings : resolution of signal phase
	const long long PHASE_POWER = 30;
	const long long PHASE_RANGE = (1 << PHASE_POWER);
public:
	// settings: central frequency of incomming and outgoing signal
	long radioFrequencyOut;
	long radioFrequencyIn;

	// settings: sample rates
	long inputRate;
	long outputRate;

	// state: signal
	IQ currentSample;

	// state: timing
	long long n = 0;
	long long itterNStep;
	long long bufferNStep;
	// current : delay change
	long long delayNStep = 0;

	// setting: timing resolution
	const int subCycles = 10000;

	// state: phase
	long unitStepPhase;
	long unitPhase;

	// current: power
	int power = 1;

	// state: timing controle
	long long last_set_delay = 0;
	long long last_target = 0;

	// current: offset n per meter
	long long dx = 0, dy = 0, dz = 0;
#ifdef RELATIVE_MOVE
	long long dxn = 0, dyn = 0, dzn = 0; // current ofset in n (state)
	long long dnstep = 1; // how fast to go to target (setting)
	long long dxmm = 0, dymm = 0, dzmm = 0; // offset in mm (current/setting)
#endif

	// settings: data flow
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

	/// <summary>
	/// Delay in miliseconds to delay in n
	/// </summary>
	/// <param name="delay_ms">delay in miliseconds</param>
	/// <returns>delay in n</returns>
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

	/// <summary>
	/// step of n per sample to corespoding phase step
	/// </summary>
	/// <param name="n"></param>
	/// <returns></returns>
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
		//std::cout << "start delay: " << std::setprecision(10) << delay_ms << std::endl;
#ifdef SET_DELAY_ON_START
		// n time
		long long new_delay = calcDelayNum(delay_ms);
		//std::cout << "old: " << n;
		n = n + last_set_delay - new_delay;
		last_set_delay = new_delay;
		lastDelay = new_delay;
		last_target = new_delay;
#endif
	}


	void setDelayTarget(double delay_ms, double time_till_next_update) {
		setDelayTargetClosedLoop(delay_ms, time_till_next_update);
	}

	long long lastDelay = 0;
	double stepFraction = 0;
	/// <summary>
	/// Calculate delay step in n per sample using the open loop methode.
	/// mainly used to test the methode
	/// </summary>
	/// <param name="delay_ms">next delay in miliseconds</param>
	/// <param name="time_till_next_update">time after witch the target delay has to be reached</param>
	void setDelayTargetOpenLoop(double delay_ms, double time_till_next_update) {


		//std::cout << "Predicted: " << lastDelay << ", Real:" << last_set_delay << ", pred error: " << last_set_delay-lastDelay << ", target: " << std::setprecision(12) << delay_ms << std::endl;

		long long nextDelay = calcDelayNum(delay_ms);
		long long addedDelay = nextDelay - last_set_delay;// lastDelay; // --> use lastDelay for actualy open loop, and last_set_delay for closed loop
		long long nStep = ((double)addedDelay * itterNStep) / (bufferNStep * inputRate * time_till_next_update + addedDelay);
		double ud = (bufferNStep * inputRate * time_till_next_update) / (itterNStep - nStep)+stepFraction;
		long long u = ceil(ud);
		stepFraction = ud - u;
		lastDelay = lastDelay + u * nStep;

		delayNStep = nStep;

		//std::cout << "target error: " << last_target - last_set_delay << ", target change: " << last_target - nextDelay << std::endl;

		last_target = nextDelay;

		//std::cout << "step: " << nStep << ", addedDelay: " << addedDelay << ", loops:" << u << std::endl;
	}


	/// <summary>
	/// Calculate delay step in n per sample using the closed loop methode.
	/// Recomened for use in the C++ implementation
	/// </summary>
	/// <param name="delay_ms">next delay in miliseconds</param>
	/// <param name="time_till_next_update">time after witch the target delay has to be reached</param>
	void setDelayTargetClosedLoop(double delay_ms, double time_till_next_update) {

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
		//std::cout << delayNStep << std::endl;

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

	/// <summary>
	/// Get the next sample
	/// This function handles the upsampleing, delaying, and frequency shifting.
	/// </summary>
	/// <returns>IQ sample</returns>
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