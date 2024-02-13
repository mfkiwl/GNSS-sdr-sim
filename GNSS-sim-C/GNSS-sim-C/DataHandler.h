#pragma once

#include <queue>
#include <stdint.h>

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
public:
	Resample* resample;

	DataHandler(int bitsPerFrame) : bitsPerFrame(bitsPerFrame) {}

	uint8_t nextBit() {
		currentBit++;
		if (currentBit == bitsPerFrame) {
			currentBit = 0;
			currentData = data.front();
			data.pop();
			resample->setDopler(currentData.doppler);
			resample->setPower(currentData.power);
			resample->setDelayTarget(data.front().delay, 0.1);
		}
		return (currentData.bits >> currentBit) & 1;
	}

	IQ nextSample() {
		return resample->nextSample();
	}

	void init() {
		currentBit = bitsPerFrame - 1;
		resample->setDelay(data.front().delay);
		resample->init();
	}

	void addFrame(DataFrame frame) {
		data.push(frame);
	}
};