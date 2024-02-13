#pragma once

#include <string>

#include "ChainLink.h"

struct Satellite {
	std::string name;

public:
	virtual ChainLink* getModulation(ChainLink* dataSource) = 0;
	virtual int getModulationRate() = 0;
	virtual long getRadioFrequency() = 0;
	virtual int getFrameSize() = 0;

	std::string getName() {
		return name;
	}
};