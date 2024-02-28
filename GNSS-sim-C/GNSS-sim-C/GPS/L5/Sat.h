#pragma once

#include <string>
#include <sstream>
#include <iomanip>
#include <vector>

#include "../../Satellite.h"
#include "Modulation.h"

namespace gps {
	namespace L5 {

		class Sat : public Satellite {
		public:
			Sat(int prn) : Satellite(prn) {
				std::stringstream ss;
				ss << "G5_" << std::setw(2) << std::setfill('0') << prn;
				name = ss.str();
			}

			virtual ChainLink* getModulation(ChainLink* dataSource) {
				Modulation* mod = new Modulation(dataSource, prn);
				return mod;
			}

			virtual int getModulationRate() {
				return 10230000;
			}

			virtual long getRadioFrequency() {
				return 1176450000;
			};

			virtual int getFrameSize() {
				return 10;
			}
		};

	}
}
