#pragma once

#include <iostream>
#include <stdint.h>

#include "../ChainLink.h"

#include "PRN_Code.h"

namespace gps {

	class Modulation : public ChainLink {
	private:

		int step = 0;
		int chip = 0;
		int repeat = 0;

		int Crepeat = 20;
		int Cchip = 1;
		int Cprn = 1023;

		PRN prn;

		ChainLink* dataSource;
		uint8_t currentData;

	public:
		Modulation(ChainLink* dataSource, int prn) : dataSource(dataSource), prn(prn) {
			step = 0;
			chip = 0;
		}

		float next() {
			if (step == Cchip) {
				chip++;
				step = 0;
			}

			if (chip == Cprn) {
				chip = 0;
				repeat++;
				prn.reset();
				//std::cout << "symbol: " << bit << " / " << length << std::endl;
			}

			if (repeat == Crepeat) {
				repeat = 0;
				currentData = dataSource->nextBit();
			}

			float v = (currentData ^ prn.next()) * 2 - 1;

			step++;

			return v;
		}

		IQ nextSample() {
			IQ iq(next());
			return iq;
		}

		void init() {
			currentData = dataSource->nextBit();
		}

		uint8_t nextBit() {
			return 0;
		}
	};

}