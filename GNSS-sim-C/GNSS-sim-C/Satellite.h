#pragma once

#include <string>

#include "ChainLink.h"

/// <summary>
/// Datastructure to encode data abbout a satalite signal
/// used to setup and configure processing chains
/// </summary>
struct Satellite {
	std::string name;
	int prn;

public:
	virtual ChainLink* getModulation(ChainLink* dataSource) = 0;
	virtual int getModulationRate() = 0;
	virtual long getRadioFrequency() = 0;
	virtual int getFrameSize() = 0;

	Satellite(int prn): prn(prn) {}

	std::string getName() {
		return name;
	}
};