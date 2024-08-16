#pragma once

#include <stdint.h>

/// <summary>
/// Data for 0.1 seconds of signal for one satellite.
/// </summary>
struct DataFrame {

	uint64_t bits;

	/// <summary>
	/// Delay at the start of the first bit in this frame
	/// </summary>
	double delay;

	double doppler;

	int power;

	/// <summary>
	/// How the delay changes as you move along an axis
	/// </summary>
	float dx,dy,dz;
};