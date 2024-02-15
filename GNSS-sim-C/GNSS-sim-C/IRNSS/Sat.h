#pragma once

#include <string>
#include <sstream>
#include <iomanip>
#include <vector>

#include "../Satellite.h"

#include "Modulation.h"

namespace irnss {

	class Sat : public Satellite {
		int prn;
	public:
		Sat(int prn) : prn(prn) {
			std::stringstream ss;
			ss << "I" << std::setw(2) << std::setfill('0') << prn;
			name = ss.str();
		}

		virtual ChainLink* getModulation(ChainLink* dataSource) {
			Modulation* mod = new Modulation(dataSource, prn);
			return mod;
		}

		virtual int getModulationRate() {
			return 1023000; // SPS signal: only data BPSK, RS signal used pilot and data BOC(5, 2)
			// BOC(5, 2) chip: 1:->10101, 0:->01010, 2xGPS chip frequency ?
		}

		virtual long getRadioFrequency() {
			return 1176450000;
		};

		virtual int getFrameSize() {
			return 5;
		}
	};

}
