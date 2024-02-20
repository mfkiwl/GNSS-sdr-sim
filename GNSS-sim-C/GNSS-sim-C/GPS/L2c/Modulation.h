#pragma once

#include "../../ChainLink.h"

namespace gps {
	namespace L2c {

		class Modulation : public ChainLink {
		private:

			PRN prnM;
			PRN prnL;

			int step = 0;
			int chipM = 0;
			int chipL = 0;
			int repeat = 0;
			int bit = 0;

			int Crepeat = 1;
			int Cchip = 12;
			int CprnM = 10230; // data
			int CprnL = 767250; // pilot (75x data)

			ChainLink* dataSource;
			uint8_t currentData;

		public:
			Modulation(ChainLink* dataSource, int prn) : dataSource(dataSource), prn(prn) {
			}

			IQ nextSample() {
				if (step  == Cchip) { step  = 0; chipL++; chipM++; }
				if (chipL == CprnL) { chipL = 0; prnL.reset(); }
				if (chipM == CprnM) { chipM = 0; prnM.reset();  currentData = dataSource->nextBit(); }

				uint8_t d;
				if (step % 2 == 0) {
					d = prnM.next() ^ currentData;
				}
				else {
					d = prnL.next();
				}

				IQ v(
					0,d*2.0-1
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