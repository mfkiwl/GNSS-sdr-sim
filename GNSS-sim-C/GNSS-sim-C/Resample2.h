#pragma once

#include <climits>

#include "IQ.h"
#include "ChainLink.h"

struct delayPolinomal {
	double a;
	double b;
	double c;

	double d;
	double e;

	const double k = 100;

	delayPolinomal() {}
	void fromDelays(double u, double v, double w) {
		a = (u + w - 2 * v) / (2 * k*k);
		b = (w - u) / (2 * k) +1;
		c = v;

		d = ((w+k) - v) / k;
		e = v;
	}
	double QdelayAt(double t) {
		return (-b + sqrt(b * b - 4 * a * (c - t))) / (2 * a);

	}
	double EdelayAt(double t) {
		return (t - e) / d;
	}
};

class Resample : public ChainLink {
	const long long PHASE_POWER = 30;
	const long long PHASE_RANGE = (1 << PHASE_POWER);
public:
	long radioFrequencyOut;
	long radioFrequencyIn;

	long inputRate;
	long outputRate;

	ChainLink* dataSource;
	ChainLink* sampleSource;

	long unitStepPhase;
	long unitPhase;

	int power = 1;

	IQ* sampleBuffer = nullptr;
	int sampleCount = 0;

	delayPolinomal delayPol, nextDelayPol;

	Resample() {
	}

	void fillSampleBuffer() {
		for (int i = 0; i < inputRate / 10; i++) {
			sampleBuffer[i] = sampleSource->nextSample();
		}
	}

	void init() {
		sampleBuffer = new IQ[inputRate/10];
		sampleCount = 0;// outputRate / 10 - 1;

		setDopler(0);

		sampleSource->init();

		fillSampleBuffer();
	}

	~Resample() {
		if (sampleBuffer != nullptr) {
			delete sampleBuffer;
		}
	}

	void setDopler(float f) {
		int64_t scale = 100;
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

	uint8_t nextBit() {
		return dataSource->nextBit();
	}


	void setDelay(double delay_ms) {
		std::cout << "delay:" << delay_ms << std::endl;
	}


	void setDelayTarget(double delay_ms, double time_till_next_update) {
		//std::cout << "delay target:" << delay_ms << std::endl;
	}

	void setDelays(double u, double v, double w) {
		//std::cout << "set delays " << u << " " << v << " " << w << std::endl;
		// u: delay of pervius 0.1s
		// v: delay at start of next 0.1s
		// w: delay at end of next 0.1s
		delayPol.fromDelays(u, v, w);

		//std::cout << delayPol.EdelayAt(v) << ", " << delayPol.EdelayAt(w) << std::endl;
	}

	IQ nextSample() {
		sampleCount++;

		//if (sampleCount == outputRate / 10) {
		//	sampleCount = 0;
			//fillSampleBuffer(); // should not be coupled to sample count but to if delayed source index overruns
		//}
		IQ sample;

		// sampleCount to time
		// get delay at time
		double time_ms = sampleCount * 1000.0 / outputRate;
		double index_time_ms = delayPol.EdelayAt(time_ms); // k=1
		//std::cout << sampleCount << " : " << time_ms << " -> " << index_time_ms;
		if (index_time_ms < 0) {
			//std::cout << " early" << std::endl;
			sample = IQ(0);
		}
		else if (index_time_ms < 100) {
			//index_time_ms = delayPol.QdelayAt(time_ms); // --> better interpolation?
			long long input_index = inputRate * (index_time_ms / 1000.0);
			//std::cout << "/" << index_time_ms << " i: " << input_index << std::endl;
			sample = sampleBuffer[input_index];
		}
		else { // index_time_ms >=100
			fillSampleBuffer();
			//std::cout << " refill" << std::endl;
			sampleCount -= outputRate / 10;
			sample = sampleBuffer[0];
		}
		// if indexFraction > 1 => fill sample buffer, indexFraction--
		//        \-> add offset?



		sample = sample.rotate((unitPhase / (float)PHASE_RANGE/*(LONG_MAX / 2)*/) * 2 * M_PI);

		unitPhase += unitStepPhase;
		while (unitPhase > PHASE_RANGE/*(LONG_MAX / 2)*/) {
			unitPhase -= PHASE_RANGE;// (LONG_MAX / 2);
		}
		while (unitPhase < 0) {
			unitPhase += PHASE_RANGE;// (LONG_MAX / 2);
		}
		return sample * power / 100;
	}
};