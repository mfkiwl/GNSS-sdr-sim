#pragma once
#include <stdint.h>
#include "IQ.h"

/// <summary>
/// Interface how processing blocks are linked together.
/// Samples go one direction along the chian, bits the other
/// </summary>
class ChainLink {
public:
	virtual uint8_t nextBit() = 0;
	virtual IQ nextSample() = 0;
	virtual void init() = 0;
};