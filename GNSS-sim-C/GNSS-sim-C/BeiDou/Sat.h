#pragma once

#include <string>
#include <sstream>
#include <iomanip>
#include <vector>

#include "../Satellite.h"

#include "Modulation.h"

namespace beidou {

	class Sat : public Satellite {
	public:
		Sat(int prn) : Satellite(prn) {
			std::stringstream ss;
			ss << "B" << std::setw(2) << std::setfill('0') << prn;
			name = ss.str();
		}

		virtual ChainLink* getModulation(ChainLink* dataSource) {
			Modulation* mod = new Modulation(dataSource, prn);
			return mod;
		}

		virtual int getModulationRate() {
			return 2046000;
		}

		virtual long getRadioFrequency() {
			return 1561098000;
		};

		virtual int getFrameSize() {
			if (prn < 6) {
				return 50; // D2
			}
			else {
				return 5; // D1
			}
		}
	};

}
