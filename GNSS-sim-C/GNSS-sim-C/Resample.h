#pragma once

#include <climits>

#include "IQ.h"
#include "ChainLink.h"

#define SET_DELAY_ON_START

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
	int subCycles = 10000;

	long unitStepPhase;
	long unitPhase;

	int power = 1;

	long long last_set_delay = 0;

	ChainLink* dataSource;
	ChainLink* sampleSource;
public:

	

	Resample(): currentSample(0.0f) {
		//init();
	}

	void init() {
		itterNStep = subCycles * (long long)inputRate;// *(targetFrequency / (double)radioFrequency); // might trow of updating of delay
		bufferNStep = subCycles * (long long)outputRate;

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
		int64_t dopplerShift = f * scale;
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

	void print_info() {
		//std::cout << targetFrequency << "/" << radioFrequencyOut << std::endl;
		//std::cout << std::setprecision(15) << targetFrequency / (double)radioFrequencyOut << std::endl;
		std::cout << itterNStep / (float)subCycles << " <- " << inputRate << " (" << itterNStep - inputRate * subCycles << ")" << std::endl;
		//std::cout << std::setprecision(15) << "Phase Delta: " << normalPhaseSampleDelta << " $ " << unitStepPhase << std::endl;
		std::cout << "frequency: " << radioFrequencyIn << std::endl;
		std::cout << std::endl;
	}

	uint8_t nextBit() {
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


		static long long last_target = 0;

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
		if (n >= bufferNStep) {
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


		sample = sample.rotate((unitPhase / (float)PHASE_RANGE/*(LONG_MAX / 2)*/) * 2 * M_PI);

		unitPhase += unitStepPhase;
		while (unitPhase > PHASE_RANGE/*(LONG_MAX / 2)*/) {
			unitPhase -= PHASE_RANGE;// (LONG_MAX / 2);
		}
		while (unitPhase < 0) {
			unitPhase += PHASE_RANGE;// (LONG_MAX / 2);
		}
		return sample * power/100;
	}
};