#pragma once

#include <stdint.h>

namespace beidou {

	int taps1[] = { 0, 1, 1, 1, 1, 1, 1,  1,  1, 2, 3, 3, 3, 3, 3,  3,  3, 4, 4, 4, 4, 4,  4,  5, 5, 5, 5,  5,  6, 6, 6,  6,  8, 8,  8,  9,  9,  10 };
	int taps2[] = { 0, 3, 4, 5, 6, 8, 9, 10, 11, 7, 4, 5, 6, 8, 9, 10, 11, 5, 6, 8, 9, 10, 11, 6, 8, 9, 10, 11, 8, 9, 10, 11, 9, 10, 11, 10, 11, 11 };

	class PRN {
		int regG1;
		int regG2;

		int tap1;
		int tap2;

	public:
		PRN(int tap1, int tap2) : tap1(tap1), tap2(tap2) {
			reset();
		}

		PRN(int prn) {
			tap1 = taps1[prn];
			tap2 = taps2[prn];
			reset();
		}

		void reset() {
			regG1 = 0b01010101010 << 1;
			regG2 = 0b01010101010 << 1;
		}

		uint8_t next() {
			regG1 |= ((regG1 >> 1) & 1) ^ ((regG1 >> 7) & 1) ^ ((regG1 >> 8) & 1) ^ ((regG1 >> 9) & 1) ^ ((regG1 >> 10) & 1) ^ ((regG1 >> 11) & 1);

			regG2 |= ((regG2 >> 1) & 1) ^ ((regG2 >> 2) & 1) ^ ((regG2 >> 3) & 1) ^ ((regG2 >> 4) & 1) ^ ((regG2 >> 5) & 1) ^ ((regG2 >> 8) & 1) ^ ((regG2 >> 9) & 1) ^ ((regG2 >> 11) & 1);

			uint8_t v = ((regG1 >> 11) & 1) ^ ((regG2 >> tap1) & 1) ^ ((regG2 >> tap2) & 1);

			regG1 = regG1 << 1;
			regG2 = regG2 << 1;

			return v;
		}

	};

}
