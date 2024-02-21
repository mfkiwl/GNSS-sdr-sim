#pragma once

#include "FileSource.h"

void generateFPGA_data(std::string fileName, unsigned long radioFrequency, unsigned long outputRate, uint64_t subCycles) {
	FileSource fileSource(fileName);
	std::vector<Satellite*> sats = fileSource.getSats();

	std::cout << "radioFrequency: " << radioFrequency << ", outputRate: " << outputRate << ", subCycles: " << subCycles << std::endl;

	int n = 0;
	std::map<std::string, DataFrame> data;
	do {
		n++;
		int i = 0;
		for (auto& sat : sats) {
			DataFrame dataFrame = data[sat->getName()];
			unsigned long targetFrequency = sat->getRadioFrequency() + dataFrame.doppler;
			uint64_t bits = dataFrame.bits;
			double delay = dataFrame.delay;
			int power = dataFrame.power;
			int prn = sat->prn;

			std::stringstream ss;
			ss << std::setw(16) << std::setfill('0') << std::hex << bits;
			std::string hexBits = ss.str();

			double delay_samples = delay / 1000 * outputRate;
			uint64_t delay_n = (subCycles * sat->getModulationRate()) * delay_samples;

			std::stringstream ss2;
			ss2 << std::setw(16) << std::setfill('0') << std::hex << delay_n;
			std::string hexDelay = ss2.str();

			int PHASE_POWER = 30;
			unsigned long PHASE_RANGE = 1<<PHASE_POWER; // 2 ^ 30

			int scale = 100;
			targetFrequency *= scale;
			long shift = targetFrequency - radioFrequency * scale;
			double normalPhaseSampleDelta = shift / (double)outputRate;
			uint32_t unitStepPhase = normalPhaseSampleDelta / scale * (PHASE_RANGE);
			
			int k = 1;
			if (power != 0) {
				//std::cout << "delay: " << delay << std::endl;
				//printf("send(%i, x\"%s\", x\"%s\", %li, %i);\n", /*prn*/ i, hexBits.c_str(), hexDelay.c_str(), unitStepPhase, /*power*/ 250/k);
				std::cout << "0x" << hexBits.c_str() << ", " << std::setprecision(10) << delay << ", " << std::setprecision(6) << dataFrame.doppler << ", " << 250 << ", " << i << ", " << sat->getRadioFrequency() <<  std::endl;
				i++;
				if (i >= k) {
					break;
				}
			}
		}
		if (n == 10) {
			break;
		}
		data = fileSource.nextData();
	} while (data.size()>0);

}

/*
struct DataFrame { // VHDL
  uint8_t satNum;
  uint64_t bits;
  int64_t delay;
  int32_t phaseStep;
  uint8_t power;
}; // 176 bits
*/