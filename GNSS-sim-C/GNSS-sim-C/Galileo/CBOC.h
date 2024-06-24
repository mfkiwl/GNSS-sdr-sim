#pragma once

#define _USE_MATH_DEFINES
#include<math.h>
#include <stdint.h>
#include"PRN_Code.h"
#include "../ChainLink.h"

//#define USE_CBOC

namespace galileo {

	class CBOC : public ChainLink {
	public:
		const int Ra = 1023000;
		const int Rb = 6138000;
		const int Rchip = 1023000;

#ifdef USE_CBOC
		const int frequency = 2 * Rb;
#else
		const int frequency = 2 * Ra;
#endif

		ChainLink* dataSource;
		uint8_t currentData;

	private:
		Prn prnData;
		Prn prnPilot;
		uint8_t* pilotData;
		size_t pilotLength;


		const float alpha = sqrt(10.0f / 11.0f);
		const float beta = sqrt(1.0f / 11.0f);

		const int Ca = frequency / Ra / 2;
		const int Cb = frequency / Rb / 2;

#ifdef USE_CBOC
		int Cchip = 12; // CBOC
#else
		int Cchip = 2; // BOC(1,1)
#endif // USE_CBOC

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



		IQ_v next() {
			if (step == Cchip) {
				chip++;
				step = 0;
			}

			if (chip == Cprn) {
				chip = 0;
				bit++;
				if (bit == pilotLength) {
					bit = 0;
				}
				currentData = dataSource->nextBit();
			}


#ifdef USE_CBOC // CBOC
			IQ_v sub_carrier_data = (((step / Ca) % 2 == 0) ? alpha * IQ_v_unit : -alpha * IQ_v_unit)
				+ (((step / Cb) % 2 == 0) ? beta * IQ_v_unit : -beta * IQ_v_unit);
			IQ_v sub_carrier_pilot = (((step / Ca) % 2 == 0) ? alpha * IQ_v_unit : -alpha * IQ_v_unit)
				- (((step / Cb) % 2 == 0) ? beta * IQ_v_unit : -beta * IQ_v_unit);
#else
			IQ_v sub_carrier_data = (((step / Ca) % 2 == 0) ? alpha * IQ_v_unit : -alpha * IQ_v_unit);
			IQ_v sub_carrier_pilot = (((step / Ca) % 2 == 0) ? alpha * IQ_v_unit : -alpha * IQ_v_unit);
#endif

			step++;

			//std::cout << (int)(sub_carrier_data*60) << " _ " << (int)(sub_carrier_pilot*60) << std::endl;

			bool prn_data = prnData.test(chip);
			bool prn_pilot = prnPilot.test(chip);
			//if (step == 1) {
			//	std::cout << "D:" << (int)prn_data << "  P:" << (int)prn_pilot << " S:" << (int)pilotData[pilotLength] << " v:" << (int)currentData << std::endl;
			//}

#ifdef USE_CBOC // CBOC
			return (
					sub_carrier_data  * (prn_data  ? -1 : 1) * (currentData    == 1 ? -1 : 1)
				  - sub_carrier_pilot * (prn_pilot ? -1 : 1) * (pilotData[bit] == 1 ? -1 : 1) // + or - ?
				  )/2;
#else
			return (
				sub_carrier_data * (prn_data ? -1 : 1) * (currentData == 1 ? -1 : 1)
				- sub_carrier_pilot * (prn_pilot ? -1 : 1) * (pilotData[bit] == 1 ? -1 : 1)
				) / 2;
#endif
		}

		IQ nextSample() {
			IQ_v v = next();
			//std::cout << (int)(v*120) << std::endl;
			IQ iq(v);
			//std::cout << step << iq << std::endl;
			return iq;
		}

		void init() {
			currentData = dataSource->nextBit();
			//std::cout << "v: " << (int)currentData << ", p: " << (int)pilotData[bit] << std::endl;
		}

		uint8_t nextBit() {
			return 0;
		}

	};
}