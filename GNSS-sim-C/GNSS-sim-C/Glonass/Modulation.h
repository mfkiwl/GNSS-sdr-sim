#pragma once

#include <iostream>
#include <stdint.h>
#include "../ChainLink.h"

namespace glonass {

	uint8_t ranging_code[511];

	// 511 000 hz
	// 511 chips long -> 1ms
	void generateRangingCode() {
		int shift = 0b1111111110;
		for (int i = 0; i < 511; i++) {
			shift |= ((shift >> 5) & 1) ^ ((shift >> 9) & 1);
			uint8_t out = (shift >> 7) & 1;
			shift = shift << 1;
			ranging_code[i] = out;
			//std::cout << (int)out;
		}
	}

	class Modulation : public ChainLink {
	private:

		int step = 0;
		int chip = 0;
		int repeat = 0;
		//int bit = 0;

		int Crepeat = 10;
		int Cchip = 1;
		int Cprn = 511;

		ChainLink* dataSource;
		uint8_t currentData;

	public:
		Modulation(ChainLink* dataSource) : dataSource(dataSource) {
			static bool ranging_code_is_generated = false;
			if (!ranging_code_is_generated) {
				generateRangingCode();
				ranging_code_is_generated = true;
			}

			step = 0;
			chip = 0;
			//bit = 0;
		}

		IQ_v next() {
			if (step == Cchip) {
				chip++;
				step = 0;
			}

			if (chip == Cprn) {
				chip = 0;
				repeat++;
				//std::cout << "symbol: " << bit << " / " << length << std::endl;
			}

			if (repeat == Crepeat) {
				repeat = 0;
				currentData = dataSource->nextBit();
				//bit++;
			}

			//if (bit == length) {
			//	bit = 0;
			//}


			IQ_v v = ((currentData ^ ranging_code[chip]) * 2 - 1)*IQ_v_unit;

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