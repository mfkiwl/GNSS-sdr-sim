#pragma once

#include <string>
#include <sstream>
#include <iomanip>
#include <vector>

#include "Modulation.h"

#include "../../Satellite.h"

namespace beidou {
	namespace B1c {

		class Sat : public Satellite {
		public:
			Sat(int prn) : Satellite(prn) {
				std::stringstream ss;
				ss << "B1c" << std::setw(2) << std::setfill('0') << prn;
				name = ss.str();
			}

			virtual ChainLink* getModulation(ChainLink* dataSource) {
				Modulation* mod = new Modulation(dataSource, prn);
				return mod;
			}

			virtual int getModulationRate() {
				return 12276000;
			}

			virtual long getRadioFrequency() {
				return 1575420000;
			};

			virtual int getFrameSize() {
				return 10;
			}
		};
	}
}