#pragma once
#include <cstdint>



namespace gps {
	namespace L2c {

		// prn 159-168(-210) (octal: '0'prefix)
		uint32_t resetMedium[] = {0604055104, 0157065232, 0013305707, 0603552017, 0230461355, 0603653437, 0652346475, 0743107103, 0401521277, 0167335110};
		uint32_t resetLong[]   = {0605253024, 0063314262, 0066073422, 0737276117, 0737243704, 0067557532, 0227354537, 0704765502, 0044746712, 0720535263};

		class PRN {

			uint32_t reg;
			uint32_t regReset;

		public:
			PRN(int prn, bool isLong) {
				if (prn >= 159) {
					prn -= 159;
				}
				if (isLong) {
					regReset = resetLong[prn];
				}
				else {
					regReset = resetMedium[prn];
				}
				reset();
			}
			
			void reset() {
				reg = regReset << 1;
			}

			uint8_t next() {
				reg |= ((reg >> 3) & 1)
					^ ((reg >>  4) & 1)
					^ ((reg >>  5) & 1)
					^ ((reg >>  6) & 1)
					^ ((reg >>  9) & 1)
					^ ((reg >> 11) & 1)
					^ ((reg >> 13) & 1)
					^ ((reg >> 16) & 1)
					^ ((reg >> 19) & 1)
					^ ((reg >> 21) & 1)
					^ ((reg >> 24) & 1)
					^ ((reg >> 27) & 1);

				uint8_t v = ((reg >> 27) & 1);

				reg = reg << 1;

				return v;
			}


		};

	}
}