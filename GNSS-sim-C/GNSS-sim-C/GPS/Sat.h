#pragma once

#include <string>
#include <sstream>
#include <iomanip>
#include <vector>

#include "../Satellite.h"

#include "Modulation.h"

namespace gps {

	class Sat : public Satellite {
		int prn;
	public:
		Sat(int prn) : prn(prn) {
			std::stringstream ss;
			ss << "G" << std::setw(2) << std::setfill('0') << prn;
			name = ss.str();
		}

		virtual ChainLink* getModulation(ChainLink* dataSource) {
			Modulation* mod = new Modulation(dataSource, prn);
			return mod;
		}

		virtual int getModulationRate() {
			return 1023000;
		}

		virtual long getRadioFrequency() {
			return 1575420000;
		};

		virtual int getFrameSize() {
			return 5;
		}
	};

}
