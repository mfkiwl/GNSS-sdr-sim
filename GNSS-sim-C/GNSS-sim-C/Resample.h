#pragma once

#include "IQ.h"
#include "ChainLink.h"

class Resample : public ChainLink{
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
	int subCycles = 1000000;

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
		int scale = 100;
		//std::cout << "setDopler" << std::endl;
		long dopplerShift = f * scale;
		long targetFrequency = dopplerShift + radioFrequencyIn * scale;
		long shift = targetFrequency - radioFrequencyOut * scale;
		double normalPhaseSampleDelta = shift / (double)outputRate;
		unitStepPhase = normalPhaseSampleDelta / scale * (LONG_MAX / 2);
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
		return ((long long)subCycles * inputRate)/*itterNStep*/ * delay_samples;
	}

	void setDelay(double delay_ms) {
		// n time
		long long new_delay = calcDelayNum(delay_ms);
		//std::cout << "old: " << n;
		n = n + last_set_delay - new_delay;
		last_set_delay = new_delay;
	}

	void setDelayTarget(double delay_ms, double time_till_next_update) {
		long long new_delay = calcDelayNum(delay_ms);
		long long last_delay = this->last_set_delay;
		long long samples_inbetween = this->outputRate * time_till_next_update;
		long long delay_change = new_delay - last_delay;
		//long long delay_change = last_delay - new_delay;
		delayNStep = delay_change / samples_inbetween;
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

		sample = sample.rotate((unitPhase / (float)(LONG_MAX / 2)) * 2 * M_PI);

		unitPhase += unitStepPhase;
		while (unitPhase > (LONG_MAX / 2)) {
			unitPhase -= (LONG_MAX / 2);
		}
		while (unitPhase < 0) {
			unitPhase += (LONG_MAX / 2);
		}
		return sample * power/100;
	}
};