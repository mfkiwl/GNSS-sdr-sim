#pragma once

#include <stdint.h>

struct DataFrame {
	uint64_t bits;
	double delay;
	double doppler;
	int power;
	float dx;
	float dy;
	float dz;
};