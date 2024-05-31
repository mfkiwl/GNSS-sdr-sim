#pragma once

#include <sstream>
#include <iomanip>

//#define USE_CBOC

#include "../Satellite.h"
#include "CBOC.h"
#include "PRN_Code.h"

namespace galileo {

	auto prnB_codes = galileo::getPRNCodes("../../data/Galileo/C7_E1B.txt");
	auto prnC_codes = getPRNCodes("../../data/Galileo/C8_E1C.txt");

	class Sat : public Satellite {
	public:

		Sat(int prn): Satellite(prn) {
			std::stringstream ss;
			ss << "E" << std::setw(2) << std::setfill('0') << prn;
			name = ss.str();
		}

		ChainLink* getModulation(ChainLink* dataSource) {
			std::stringstream ssB;
			ssB << "E1B__Code_No_" << std::setw(2) << std::setfill('0') << prn;
			std::stringstream ssC;
			ssC << "E1C__Code_No_" << std::setw(2) << std::setfill('0') << prn;
			CBOC* modulation = new CBOC(prnB_codes.at(ssB.str()), prnC_codes.at(ssC.str()), SC25_uint8, SC25_length);
			modulation->dataSource = dataSource;
			return modulation;
		}

		int getModulationRate() {
#ifdef USE_CBOC
			return 2 * 6138000;
#else
			return 2 * 1023000;
#endif
		}

		long getRadioFrequency() {
			return 1575420000;
		}

		int getFrameSize() {
			return 25;
		}
	};

}