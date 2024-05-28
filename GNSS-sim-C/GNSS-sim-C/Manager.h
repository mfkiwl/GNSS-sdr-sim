#pragma once

#include <map>
#include <iostream>
#include <iterator>
#include <random>
#include <math.h>
#include <algorithm>
#include <execution>

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

	std::default_random_engine generator;
	std::normal_distribution<float> dist;
	float SNR = 1;

public:

	Manager(unsigned long sampleRate, unsigned long radioFrequency): sampleRate(sampleRate), radioFrequency(radioFrequency), dist(0.0f, 1.0f / 4.2f) {
		
	}

	void setNoise(float SNR_db) {
		float factor = powf(10.0f, SNR_db / 10);
		SNR = 1- (1 / (factor + 1));
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

	template<typename T>
	void run(FileSource& source, FileSink<T>& sink, int skip10th = 0) {
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

		// back buffer and frond buffer, fill back buffer 1 thread per each chanel, front buffer merge the chanels

		int t = 0;
		while (addData(source.nextData())) {
			t++;
			for (int i = 0; i < sampleRate / 10; i++) {
				IQ iq = next();
				sink.add(iq*SNR + IQ(dist(generator), dist(generator))* (1 - SNR));
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

	template<typename T>
	void run_paralell(FileSource& source, FileSink<T>& sink, int skip10th = 0) {
		std::vector<Satellite*> sats = source.getSats();
		int numSats = sats.size();
		for (auto& sat : sats) {
			activeSats[sat->getName()] = setupChain(sat, sampleRate, radioFrequency);
		}
		addData(source.nextData());
		addData(source.nextData());
		for (auto& sat : sats) {
			activeSats[sat->getName()]->init();
		}

		size_t buffer_size = sampleRate/10;
		std::map<std::string, IQ*>* backbuffer;
		std::map<std::string, IQ*>* frontbuffer;
		IQ* merged_buffer;
		init_paralell(buffer_size, &backbuffer, &frontbuffer, &merged_buffer);

		for (int j = 0; j < skip10th && addData(source.nextData()); j++) {
			run_paralell(buffer_size, frontbuffer);
		}


		int t = 0;
		while (addData(source.nextData())) {
			t++;
			run_paralell(buffer_size, frontbuffer);
			merge(buffer_size, frontbuffer, merged_buffer); // run merge+sink in paralell with run_paralell
			for (int i = 0; i < buffer_size; i++) {
				sink.add(merged_buffer[i]/numSats);
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

		free_paralell(buffer_size, backbuffer, frontbuffer, merged_buffer);
	}

	void init_paralell(size_t buffer_size, std::map<std::string, IQ*>** backbuffer, std::map<std::string, IQ*>** frontbuffer, IQ** merged_buffer) {
		*merged_buffer = new IQ[buffer_size];
		*backbuffer = new std::map<std::string, IQ*>;
		*frontbuffer = new std::map<std::string, IQ*>;
	}

	void free_paralell(size_t buffer_size, std::map<std::string, IQ*>* backbuffer, std::map<std::string, IQ*>* frontbuffer, IQ* merged_buffer) {
		delete merged_buffer;
		for (auto& chanel : *backbuffer) {
			delete chanel.second;
		}
		delete backbuffer;
		for (auto& chanel : *frontbuffer) {
			delete chanel.second;
		}
		delete frontbuffer;
	}

	void run_paralell(size_t buffer_size, std::map<std::string, IQ*>* buffer) {
		for (auto& sat : activeSats) {
			if (buffer->find(sat.first) == buffer->end()) {
				buffer->insert(std::make_pair(sat.first, new IQ[buffer_size]));
			}
		}
		std::for_each(
			std::execution::par,
			activeSats.begin(),
			activeSats.end(),
			[&](std::pair<std::string, DataHandler*>&& sat)
			{
				std::string satName = sat.first;
				IQ* chanel = buffer->at(satName);
				for (int i = 0; i < buffer_size; i++) {
					chanel[i] = sat.second->nextSample();
				}
			});

		//std::map<std::string, IQ*>* tmp = backbuffer;
		//backbuffer = frontbuffer;
		//frontbuffer = tmp;

	}

	void merge(size_t buffer_size, std::map<std::string, IQ*>* buffers, IQ* merged_buffer) {
		for (int i = 0; i < buffer_size; i++) {
			merged_buffer[i] = 0;
		}
		for (auto& sat : *buffers) {
			for (int i = 0; i < buffer_size; i++) {
				merged_buffer[i] = merged_buffer[i]+sat.second[i];
			}
		}
		//for (int i = 0; i < buffer_size; i++) {
		//	merged_buffer[i] = merged_buffer[i]/256;
		//}
	}

};