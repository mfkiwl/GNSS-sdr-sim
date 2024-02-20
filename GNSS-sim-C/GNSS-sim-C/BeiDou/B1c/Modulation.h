#pragma once

#include <iostream>
#include <stdint.h>

#include "PRN_Code.h"
#include "../../IQ.h"
#include "../../ChainLink.h"

namespace beidou {
	namespace B1c {

		float s_B1C_data[12];
		float s_B1C_pilot_a[12];
		float s_B1C_pilot_b[12];

		void initModulationPaterns() {
			for (int i = 0; i < 12; i++) {
				int sign_sin_a = ((i / 6) * 2 - 1);
				int sign_sin_b = ((i % 2) * 2 - 1);
				s_B1C_data[i] = sign_sin_a * 0.5f;
				s_B1C_pilot_a[i] = sign_sin_a * sqrt(29.0 / 44.0);
				s_B1C_pilot_b[i] = sign_sin_b * sqrt(1.0 / 11.0);

				std::cout << s_B1C_data[i] << ", " << s_B1C_pilot_a[i] << ", " << s_B1C_pilot_b[i] << std::endl;
			}
		}

		class Modulation : public ChainLink {
		private:


			PRN prn;

			int step = 0;
			int chip = 0;
			int repeat = 0;
			int bit = 0;

			int sec_chip = 0;

			int Crepeat = 1;
			int Cchip = 12;
			int Cprn = 10230;

			int Csec_chip = 1800;

			ChainLink* dataSource;
			uint8_t currentData;

		public:
			Modulation(ChainLink* dataSource, int prn) : dataSource(dataSource), prn(2678, 699, 796, 7575, 269, 1889) {
				// todo: propper prn assignment
			}

			// return 0 or 1;
			int8_t nextPRN_pilot() {
				return prn.getPilot(chip, sec_chip);
			}

			int8_t nextPRN_data() {
				return prn.getData(chip, sec_chip);
			}

			void resetPRN() {
				sec_chip++;
				if (sec_chip == Csec_chip) {
					sec_chip = 0;
				}
			}

			IQ nextSample() {
				if (step == Cchip)     { step   = 0; chip++;   }
				if (chip == Cprn)      { chip   = 0; repeat++; resetPRN(); }
				if (repeat == Crepeat) { repeat = 0; bit++;    currentData = dataSource->nextBit(); }
				if (bit == length)     { bit    = 0; }

				float s_data = s_B1C_data[step];
				float s_pilot_a = s_B1C_pilot_a[step];
				float s_pilot_b = s_B1C_pilot_b[step];

				int8_t d_data = -currentData * 2 + 1;

				int8_t c_data = -nextPRN_data() * 2 + 1;
				int8_t c_pilot = -nextPRN_pilot() * 2 + 1;

				IQ v(
					s_data * d_data * c_data + s_pilot_b * c_pilot,
					s_pilot_a * c_pilot
				);

				step++;
				return v;
			}

			void init() {
				currentData = dataSource->nextBit();
			}

			uint8_t nextBit() {
				return 0;
			}
		};
	}
}