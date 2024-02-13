#pragma once

#define _USE_MATH_DEFINES
#include<math.h> 
#include <stdint.h>

namespace galileo {

	float modulate(float C_E1B, float C_E1C, float D_E1B, float sc_E1B, float sc_E1C) {
		return C_E1B * D_E1B * sc_E1B + C_E1C * sc_E1C;
	}

	float R_SE1Ba = 1023000;
	float R_SE1Bb = 6138000;
	float R_SE1Ca = 1023000;
	float R_SE1Cb = 6138000;

	float R_CE1B = 1023000;
	float R_CE1C = 1023000; // chips / sec

	float chipsPerBit = 4092; // chips / bit
	float bitTime = chipsPerBit / R_CE1B; // sec / bit

	float alpha = sqrt(10.0f / 11.0f);
	float beta = sqrt(1.0f / 11.0f);

	float chip_repeat_time = chipsPerBit / R_CE1B;

	float time_to_chip_index(float t) {
		return (int)(t * R_CE1B);
	}

	float sign(float x) {
		if (x > 0) return 1;
		if (x < 0) return -1;
		return 0;
	}

	float sc(float R, float t) {
		return sign(sin(2 * M_PI * R * t));
	}

	float s_E1(float C_E1B, float C_E1C, float D_E1B, float t) {
		//float e_E1B = (( ((C_E1B+1)/-2) * ((D_E1B+1)/-2) )*2-1)*-1;
		float e_E1B = C_E1B * D_E1B;
		float e_E1C = C_E1C;
		//std::cout << e_E1B << " " << e_E1C << std::endl;
		float v = 1 / sqrt(2) * (
			e_E1B * (alpha * sc(R_SE1Ba, t) + beta * sc(R_SE1Bb, t))
			-
			e_E1C * (alpha * sc(R_SE1Ca, t) - beta * sc(R_SE1Cb, t))
			);
		//std::cout << v << " - " << t << std::endl;
		return v;
	}

	float s_E1(bool C_E1B, bool C_E1C, uint8_t D_E1B, float t) {
		return s_E1(C_E1B ? -1.0f : 1.0f, C_E1C ? -1.0f : 1.0f, D_E1B == 1 ? -1.0f : 1.0f, t);
	}

}