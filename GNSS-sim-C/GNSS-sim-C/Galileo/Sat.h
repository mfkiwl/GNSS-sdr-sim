#pragma once

#include <sstream>
#include <iomanip>

#include "../Satellite.h"
#include "CBOC.h"
#include "PRN_Code.h"

namespace galileo {

	auto prnB_codes = galileo::getPRNCodes("C:\\Users\\Mike\\Desktop\\Thesis\\Galileo\\C7_E1B.txt");
	auto prnC_codes = getPRNCodes("C:\\Users\\Mike\\Desktop\\Thesis\\Galileo\\C8_E1C.txt");

	class Sat : public Satellite {

		int prn;
	public:

		Sat(int prn): prn(prn) {
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
			return 2 * 6138000;
		}

		long getRadioFrequency() {
			return 1575420000;
		}

		int getFrameSize() {
			return 25;
		}
	};

}