#pragma once

#define _USE_MATH_DEFINES
#include<math.h>
#include <stdint.h>
#include"PRN_Code.h"
#include "../ChainLink.h"

namespace galileo {

	class CBOC : public ChainLink {
	public:
		const int Ra = 1023000;
		const int Rb = 6138000;
		const int Rchip = 1023000;

		const int frequency = 2 * Rb;

		ChainLink* dataSource;
		uint8_t currentData;

	private:
		Prn prnData;
		Prn prnPilot;
		uint8_t* pilotData;
		size_t pilotLength;


		float alpha = sqrt(10.0f / 11.0f);
		float beta = sqrt(1.0f / 11.0f);

		int Ca = frequency / Ra / 2;
		int Cb = frequency / Rb / 2;

		int Cchip = 12;
		int Cprn = 4092;

		int step;
		int chip;
		int bit;

	public:
		CBOC(Prn prnData, Prn prnPilot, uint8_t* pilotData, size_t pilotLength) {
			this->prnData = prnData;
			this->prnPilot = prnPilot;
			this->pilotData = pilotData;
			this->pilotLength = pilotLength;
			step = 0;
			chip = 0;
			bit = 0;
			//std::cout << "init chip: " << chip << " prn: " << (prn.test(chip) ? -1 : 1) << std::endl;
			//std::cout << "init bit: " << bit << " data: " << (data[bit] == 1 ? -1 : 1) << std::endl;
		}



		float next() {
			if (step == Cchip) {
				chip++;
				step = 0;
				//std::cout << "next chip: " << chip % Cprn << " prn: " << (prn.test(chip%Cprn) ? -1 : 1) << std::endl;
			}

			if (chip == Cprn) {
				chip = 0;
				bit++;
				currentData = dataSource->nextBit();
				//std::cout << "next bit: " << bit % length << " data: " << (data[bit%length] == 1 ? -1 : 1) << std::endl;
			}

			if (bit == pilotLength) {
				bit = 0;
			}

			float sub_carrier_data = (((step / Ca) % 2 == 0) ? alpha : -alpha)
				+ (((step / Cb) % 2 == 0) ? beta : -beta);
			float sub_carrier_pilot = (((step / Ca) % 2 == 0) ? alpha : -alpha)
				- (((step / Cb) % 2 == 0) ? beta : -beta);
			step++;



			return sub_carrier_data  * (prnData.test(chip)  ? -1 : 1) * (currentData            == 1 ? -1 : 1)
				 + sub_carrier_pilot * (prnPilot.test(chip) ? -1 : 1) * (pilotData[pilotLength] == 1 ? -1 : 1);
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