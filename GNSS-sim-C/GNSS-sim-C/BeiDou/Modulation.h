#pragma once

#include <iostream>
#include <stdint.h>
#include "../ChainLink.h"
#include "PRN_Code.h"

namespace beidou {

	//2.046 Mcps
	//2046 chips
	//1000 repeats per seccond
	//D1: secondary code 1000bps
	//D2: 500 bps, D1: 50 bps

	uint8_t NH_code[] = {0,0,0,0,0,1,0,0,1,1,0,1,0,1,0,0,1,1,1,0 };
	size_t NH_code_length = 20;

	class Modulation : public ChainLink {
	private:

		int step = 0;
		int chip = 0;
		int repeat = 0;
		int bit = 0;

		int Crepeat = 20; // 50 bps D1
		//int Crepeat = 2; // 500 bps D1
		int Cchip = 1;
		int Cprn = 2046;

		PRN prn;

		ChainLink* dataSource;
		uint8_t currentData;

	public:
		Modulation(ChainLink* dataSource, int prn) : dataSource(dataSource), prn(prn) {
			step = 0;
			chip = 0;

			if (prn < 6) {
				Crepeat = 2; // D2
			}
			else {
				Crepeat = 20; // D1
			}
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
			}

			if (repeat == Crepeat) {
				repeat = 0;
				currentData = dataSource->nextBit();
			}

			uint8_t prn_chip = prn.next();
			float v = (currentData ^ NH_code[repeat] ^ prn_chip) * 2 - 1;
			//std::cout << v << std::endl;
			//float v = (((currentData>>1)&1) ^ (currentData&1) ^ NH_code[repeat] ^ prn_chip) * 2 - 1; // is this how i want to handle the 2 data streams?

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