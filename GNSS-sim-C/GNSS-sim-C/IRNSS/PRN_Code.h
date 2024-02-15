#pragma once

#include <stdint.h>

namespace irnss {

	// L5

	int G1_reset[] = { 0, 0b1110100111, 0b0000100110, 0b1000110100, 0b0101110010, 0b1110110000, 0b0001101011, 0b0000010100, 0b0100110000, 0b0010011000, 0b1101100100, 0b0001001100, 0b1101111100, 0b1011010010, 0b0111101010 };

	class PRN {
		int regG1;
		int regG2;

		int prn;

	public:

		PRN(int prn) {
			this->prn = prn;
			reset();
		}

		void reset() {
			regG1 = G1_reset[prn] << 1;
			regG2 = 0b1111111111 << 1;
		}

		uint8_t next() {
			regG1 |= ((regG1 >> 3) & 1) ^ ((regG1 >> 10) & 1);

			regG2 |= ((regG2 >> 2) & 1) ^ ((regG2 >> 3) & 1) ^ ((regG2 >> 6) & 1) ^ ((regG2 >> 8) & 1) ^ ((regG2 >> 9) & 1) ^ ((regG2 >> 10) & 1);

			uint8_t v = ((regG1 >> 10) & 1) ^ ((regG2 >> 10) & 1);

			regG1 = regG1 << 1;
			regG2 = regG2 << 1;

			return v;
		}

	};

}
