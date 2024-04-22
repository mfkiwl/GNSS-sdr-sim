#pragma once

#include <map>

#include "Satellite.h"
#include "IQ.h"
#include "FileSource.h"
#include "FileSink.h"

DataHandler* setupChain(Satellite* sat, long sampleRate, long radioFrequency) {
	DataHandler* dataHandler = new DataHandler(sat->getFrameSize());

	Resample* resample = new Resample();
	resample->inputRate = sat->getModulationRate();
	resample->outputRate = sampleRate;
	resample->radioFrequencyIn = sat->getRadioFrequency();
	resample->radioFrequencyOut = radioFrequency;


	ChainLink* modulation = sat->getModulation(resample);

	resample->dataSource = dataHandler;
	resample->sampleSource = modulation;

	dataHandler->resample = resample;

	return dataHandler;
}

void deleteChain(DataHandler* dataHandler) {
	Resample* resample = dataHandler->resample;
	ChainLink* modulation = resample->sampleSource;
	delete modulation;
	delete resample;
	delete dataHandler;
}

class Manager {
private:
	std::map<std::string, DataHandler*> activeSats;

	unsigned long sampleRate = 20000000;
	unsigned long radioFrequency = 1575420000;

public:

	Manager(unsigned long sampleRate, unsigned long radioFrequency): sampleRate(sampleRate), radioFrequency(radioFrequency) {

	}

	bool addData(std::map<std::string, DataFrame> satsData) {
		if (satsData.size() == 0) {
			return false;
		}
		for (auto& sat : activeSats) {
			sat.second->addFrame(satsData[sat.first]);
		}
		return true;
	}

	IQ next() {
		int n = 0;
		IQ iq(0);
		for (auto & sat : activeSats) {
			iq = iq + sat.second->nextSample();
			n++;
		}
		return iq / n;
	}

	void run(FileSource& source, FileSink& sink, int skip10th = 0) {
		std::vector<Satellite*> sats = source.getSats();
		for (auto& sat : sats) {
			activeSats[sat->getName()] = setupChain(sat, sampleRate, radioFrequency);
		}
		addData(source.nextData());
		addData(source.nextData());
		for (auto& sat : sats) {
			activeSats[sat->getName()]->init();
		}

		for (int j = 0; j < skip10th && addData(source.nextData()); j++) {
			for (int i = 0; i < sampleRate / 10; i++) {
				next();
			}
		}

		int t = 0;
		while (addData(source.nextData())) {
			t++;
			for (int i = 0; i < sampleRate / 10; i++) {
				IQ iq = next();
				sink.add(iq);
			}
			printf("\r %.1f s", (float)t / 10.0);
			std::cout << std::flush;
			
			//std::cout << "\r" << (float)t / 10.0 << " s";
			//std::cout << "line" << std::endl;
		}
		sink.close();

		for (auto& sat : activeSats) {
			deleteChain(sat.second);
		}
		for (auto& sat : sats) {
			delete sat;
		}
		activeSats.clear();
	}

};