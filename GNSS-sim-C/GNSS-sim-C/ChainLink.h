#pragma once
#include <stdint.h>
#include "IQ.h"

class ChainLink {
public:
	virtual uint8_t nextBit() = 0;
	virtual IQ nextSample() = 0;
	virtual void init() = 0;
};