#pragma once

#include "FileSource.h"

void generateFPGA_data(std::string fileName, unsigned long radioFrequency, unsigned long outputRate, uint64_t subCycles) {
	FileSource fileSource(fileName);
	std::vector<Satellite*> sats = fileSource.getSats();

	int n = 0;
	std::map<std::string, DataFrame> data;
	do {
		n++;
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

			int scale = 100;
			targetFrequency *= scale;
			long shift = targetFrequency - radioFrequency * scale;
			double normalPhaseSampleDelta = shift / (double)outputRate;
			uint32_t unitStepPhase = normalPhaseSampleDelta / scale * (LONG_MAX / 2);
			
			if (power != 0) {
				printf("send(%i, x\"%s\", %lli, %li, %i)\n", prn, hexBits.c_str(), delay_n, unitStepPhase, power);
			}
		}
		if (n == 40) {
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