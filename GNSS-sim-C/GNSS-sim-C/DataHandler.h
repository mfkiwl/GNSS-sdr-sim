#pragma once

#include <queue>
#include <stdint.h>
#include <iomanip>

#include "IQ.h"
#include "Resample.h"
#include "DataFrame.h"
#include "ChainLink.h"

class DataHandler : public ChainLink {
private:

	std::queue<DataFrame> data;
	int bitsPerFrame;

	DataFrame currentData;
	int currentBit;

	double last_frame_delay = 0;

public:
	Resample* resample;

	DataHandler(int bitsPerFrame) : bitsPerFrame(bitsPerFrame) {}

	uint8_t nextBit() {
		currentBit++;
		if (currentBit == bitsPerFrame) {
			loadNextFrame();
			//resample->setDopler(currentData.doppler);
			//resample->setPower(currentData.power);
			//resample->setDelayTarget(data.front().delay, 0.1);
		}
		
		setBitData();

		//std::cout << resample->delayNStep << std::endl;

		/*long long actual_delay = resample->last_set_delay;
		double delayExpectation = currentData.delay / bitsPerFrame * (bitsPerFrame - (currentBit)) + data.front().delay / bitsPerFrame * (currentBit);
		long long expected_delay = resample->calcDelayNum(delayExpectation);
		long long step = resample->delayNStep;
		
		std::cout << std::setprecision(16) << "[" << delayTarget << ", " << dopplerTarget << ", " << powerTarget << ", " << actual_delay << ", " << expected_delay << ", " << step << "]," << std::endl;
		*/

		return (currentData.bits >> currentBit) & 1;
	}

	IQ nextSample() {
		return resample->nextSample();
	}

	void init() {
		currentBit = bitsPerFrame - 1;
		last_frame_delay = data.front().delay;
		currentData.delay = last_frame_delay;
		resample->setDelay(data.front().delay);
		resample->init();
	}

	void addFrame(DataFrame frame) {
		data.push(frame);
	}

	bool willBeActive() {
		return !(currentData.power == 0 && data.front().power == 0);
	}

	void skipFrame() {
		loadNextFrame();
		setBitData();
	}

private:
	void loadNextFrame() {
		currentBit = 0;
		last_frame_delay = currentData.delay;
		currentData = data.front();
		data.pop();
		resample->setDxyz(currentData.dx / 1000000, currentData.dy / 1000000, currentData.dz / 1000000);
	}

	void setBitData() {
		double u = last_frame_delay;
		double v = currentData.delay;
		double w = data.front().delay;

		double a = (u + w - 2 * v) / (2 * bitsPerFrame * bitsPerFrame);
		double b = (w - u) / (2 * bitsPerFrame);
		double c = v;

		//double delayTarget   = currentData.delay   /bitsPerFrame*(bitsPerFrame-(currentBit+1)) + data.front().delay   /bitsPerFrame*(currentBit+1);
		int x = (currentBit + 1);
		double delayTarget = a * x * x + b * x + c;
		double dopplerTarget = currentData.doppler / bitsPerFrame * (bitsPerFrame - (currentBit)) + data.front().doppler / bitsPerFrame * (currentBit);
		double powerTarget = currentData.power / bitsPerFrame * (bitsPerFrame - (currentBit)) + data.front().power / bitsPerFrame * (currentBit);
		resample->setDopler(dopplerTarget);
		resample->setPower(powerTarget);
		resample->setDelayTarget(delayTarget, 0.1 / bitsPerFrame);
	}
};