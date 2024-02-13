#pragma once

#include <string>
#include <sstream>
#include <iomanip>
#include <vector>

#include "../Satellite.h"

#include "Modulation.h"

namespace glonass {

    class Sat : public Satellite {
		int frequency_number;
	public:
		Sat(int prn, int frequency_number) : frequency_number(frequency_number) {
			std::stringstream ss;
			ss << "R" << std::setw(2) << std::setfill('0') << prn;
			name = ss.str();
		}

		virtual ChainLink* getModulation(ChainLink* dataSource) {
			Modulation* mod = new Modulation(dataSource);
			return mod;
		}

		virtual int getModulationRate() {
			return 511000;
		}
		
		virtual long getRadioFrequency() {
			return 1602000000 + 562500 * frequency_number;
		};
		
		virtual int getFrameSize() {
			return 10;
		}
    };

}