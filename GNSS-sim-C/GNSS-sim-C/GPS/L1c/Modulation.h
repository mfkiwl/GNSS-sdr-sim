#pragma once

#include "../../ChainLink.h"
#include "PRN_Code.h"

namespace gps {
	namespace L1c {

		uint8_t BOC6_1[] = { 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0 };
		uint8_t BOC1_1[] = { 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0 };

		class Modulation : public ChainLink {
		private:

			// 10 ms bit -> 100 bps
			// 1.023 Mcps
			// 10230 chips


			// overlay overlay 18 s, 100 bps, 1800


			PRN prn;

			int step = 0;
			int chip = 0;
			int repeat = 0;
			int bit = 0;

			int Crepeat = 1;
			int Cchip = 12;
			int Cprn = 10230;
			int Coverlay = 1800;
			

			ChainLink* dataSource;
			uint8_t currentData;

			uint8_t chip;
			uint8_t overlay_code;

		public:
			Modulation(ChainLink* dataSource, int prn) : dataSource(dataSource), prn(prn) {
			}

			IQ nextSample() {
				if (step   == Cchip)    { step = 0;   chip++;    chip = prn.next(); }
				if (chip   == Cprn)     { chip = 0;   repeat++;  prn.reset(); }
				if (repeat == Crepeat)  { repeat = 0; bit++;     currentData = dataSource->nextBit(); overlay_code = prn.nextOverlay(); } // not shure this logic for reset overlay works
				if (bit == Coverlay)    { bit = 0;               prn.resetOverlay(); }

				uint8_t* pilotSpreadingSymbol = BOC1_1;
				int t = chip % 33;
				if (t == 0 || t == 4 || t == 6 || t == 29) { // BOC(1,6 for pilot)
					pilotSpreadingSymbol = BOC6_1;
				}

				uint8_t d = currentData ^ overlay_code ^ (chip & 1) ^ BOC1_1[step]; // BOC(1, 1)
				uint8_t p = (chip>>1)&1 ^ pilotSpreadingSymbol[step];               // TMBOC() / BOC(1, 1) + BOC(1, 6)

				IQ v(
					0, (d+p) - 1
				);

				step++;
				return v;
			}

			void init() {
				currentData = dataSource->nextBit();
				chip = prn.next();
				overlay_code = prn.nextOverlay();
			}

			uint8_t nextBit() {
				return 0;
			}
		};

	}
}