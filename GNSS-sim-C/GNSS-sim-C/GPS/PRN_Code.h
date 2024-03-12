#pragma once

#include <stdint.h>

namespace gps {

	int taps1[] = { 0, 2, 3, 4, 5, 1, 2 , 1, 2, 3 , 2, 3, 5, 6, 7, 8, 9 , 1, 2, 3, 4, 5, 6, 1, 4, 5, 6, 7, 8 , 1, 2, 3, 4, 5 , 4 , 1, 2, 4  };
	int taps2[] = { 0, 6, 7, 8, 9, 9, 10, 8, 9, 10, 3, 4, 6, 7, 8, 9, 10, 4, 5, 6, 7, 8, 9, 3, 6, 7, 8, 9, 10, 6, 7, 8, 9, 10, 10, 7, 8, 10 };

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
			tap1 = taps1[prn % 256];
			tap2 = taps2[prn % 256];
			reset();
		}

		void reset() {
			regG1 = 0b11111111110;
			regG2 = 0b11111111110;
		}

		uint8_t next() {
			regG1 |= ((regG1 >> 3) & 1) ^ ((regG1 >> 10) & 1);

			regG2 |= ((regG2 >> 2) & 1) ^ ((regG2 >> 3) & 1) ^ ((regG2 >> 6) & 1) ^ ((regG2 >> 8) & 1) ^ ((regG2 >> 9) & 1) ^ ((regG2 >> 10) & 1);

			uint8_t v = ((regG1 >> 10) & 1) ^ ((regG2 >> tap1) & 1) ^ ((regG2 >> tap2) & 1);

			regG1 = regG1 << 1;
			regG2 = regG2 << 1;

			return v;
		}

	};

}
