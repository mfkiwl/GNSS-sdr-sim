#pragma once

#include <map>
#include <iostream>
#include <iterator>
#include <random>
#include <math.h>
#include <algorithm>
#include <execution>
#include <future>

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

/// <summary>
/// Manages a simulation by
///  - Setting up processing chains
///  - Mixing signals
///  - Handeling paralelization
///  - Handeling input and output
/// </summary>
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

	/// <summary>
	/// set noize level to be added
	/// </summary>
	/// <param name="SNR_db">Stregth compared to a solo satalite at full power</param>
	void setNoise(float SNR_db) {
		float factor = powf(10.0f, SNR_db / 10);
		SNR = 1- (1 / (factor + 1));
	}

	/// <summary>
	/// Add data to the data handels
	/// </summary>
	/// <param name="satsData">data to add</param>
	/// <returns>if data was persent</returns>
	bool addData(std::map<std::string, DataFrame> satsData) {
		if (satsData.size() == 0) {
			return false;
		}
		for (auto& sat : activeSats) {
			sat.second->addFrame(satsData[sat.first]);
		}
		return true;
	}

	/// <summary>
	/// Get the next mixed IQ sample
	/// </summary>
	/// <returns>IQ sample</returns>
	IQ next() {
		int n = 0;
		IQ iq(0);
		for (auto & sat : activeSats) {
			iq = iq + sat.second->nextSample();
			n++;
		}
		return iq / n;
	}

	/// <summary>
	/// Run simulation with satellites in serial
	/// </summary>
	/// <typeparam name="DST">type for the data sink (.add(IQ) and .close())</typeparam>
	/// <typeparam name="SRC">type for the data source (.getSats() and .nextData())</typeparam>
	/// <param name="source">Used to get data for the satellites</param>
	/// <param name="sink">Used to store the generated signal</param>
	/// <param name="skip10th">How much of the signal to skip at the start, ~0.4 second(=4) is recomended</param>
	template<typename SRC, typename DST>
	void run(SRC& source, DST& sink, int skip10th = 0) {
		// create chains
		std::vector<Satellite*> sats = source.getSats();
		for (auto& sat : sats) {
			activeSats[sat->getName()] = setupChain(sat, sampleRate, radioFrequency);
		}

		// load inital data
		addData(source.nextData());
		addData(source.nextData());
		for (auto& sat : sats) {
			activeSats[sat->getName()]->init();
		}

		// skip first part of signal
		for (int j = 0; j < skip10th && addData(source.nextData()); j++) {
			for (int i = 0; i < sampleRate / 10; i++) {
				next();
			}
		}

		// run simulation
		int t = 0;
		while (addData(source.nextData())) {
			t++;

			// temp test for dxmm
			//if (t > 150 && t < 152) {
			//	dymm = -10000;
			//	std::cout << "change offset target" << std::endl;
			//}

			for (int i = 0; i < sampleRate / 10; i++) {
				IQ iq = next();
				sink.add(iq*SNR + IQ(dist(generator), dist(generator))* (1 - SNR));
			}
			printf("\r %.1f s", (float)t / 10.0);
			std::cout << std::flush;
			
			//std::cout << "\r" << (float)t / 10.0 << " s";
			//std::cout << "line" << std::endl;
		}

		//clean up
		sink.close();

		for (auto& sat : activeSats) {
			deleteChain(sat.second);
		}
		for (auto& sat : sats) {
			delete sat;
		}
		activeSats.clear();
	}

	typedef std::map<std::string, std::pair<bool, IQ*>>* SatSampBuffer;

	/// <summary>
	/// Run simulation with satellites in paralell
	/// </summary>
	/// <typeparam name="DST">type for the data sink (.add(IQ) and .close())</typeparam>
	/// <typeparam name="SRC">type for the data source (.getSats() and .nextData())</typeparam>
	/// <param name="source">Used to get data for the satellites</param>
	/// <param name="sink">Used to store the generated signal</param>
	/// <param name="skip10th">How much of the signal to skip at the start, ~0.4 second(=4) is recomended</param>
	template<typename SRC, typename DST>
	void run_paralell(SRC& source, DST& sink, int skip10th = 0) {
		// create chains
		const size_t batches = 1;
		std::vector<Satellite*> sats = source.getSats();
		int numSats = sats.size();
		for (auto& sat : sats) {
			activeSats[sat->getName()] = setupChain(sat, sampleRate, radioFrequency);
		}

		// load inital data
		addData(source.nextData());
		addData(source.nextData());
		for (auto& sat : sats) {
			activeSats[sat->getName()]->init();
		}

		// setup buffers for paralelization
		size_t buffer_size = sampleRate/10*batches;
		SatSampBuffer backbuffer;
		SatSampBuffer frontbuffer;
		IQ* merged_buffer;
		init_paralell(buffer_size, &backbuffer, &frontbuffer, &merged_buffer);


		// skip first part of signal
		for (int j = 0; j < skip10th && addData(source.nextData()); j+=batches) {
			if (batches > 1) {
				for (int i = 0; i < batches - 1; i++) {
					if (!addData(source.nextData())) {
						break;
					}
				}
			}
			run_paralell(buffer_size, frontbuffer);
		}


		int t = 0;

		for (int i = 0; i < batches; i++) {
			if (!addData(source.nextData())) {
				break;
			}
		}
		run_paralell(buffer_size, backbuffer);
		t++;

		// run simulation
		while (addData(source.nextData())) {
			if (batches > 1) {
				for (int i = 0; i < batches - 1; i++) {
					if (!addData(source.nextData())) {
						break;
					}
					t++;
				}
			}
			t++;

#ifdef RELATIVE_MOVE
			// a quick movement at 15 seconds into the signal
			if (t > 150 && t < 152) {
				std::cout << "targed modified" << std::endl;
				for (auto& sat : activeSats) {
					sat.second->resample->dymm = -10000;
				}
			}
#endif
			
			std::future<void> run = std::async(std::launch::async, [&, buffer_size, frontbuffer]() {
				run_paralell(buffer_size, frontbuffer);
			});
			merge(buffer_size, backbuffer, merged_buffer, sink, numSats); // run merge+sink in paralell with run_paralell
			run.get();
					

			auto tmp = frontbuffer;
			frontbuffer = backbuffer;
			backbuffer = tmp;

			printf("\r %.1f s", (float)t / 10.0);
			std::cout << std::flush;

			//std::cout << "\r" << (float)t / 10.0 << " s";
			//std::cout << "line" << std::endl;
		}

		merge(buffer_size, backbuffer, merged_buffer, sink, numSats); // run merge+sink in paralell with run_paralell

		// clean up
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

	void init_paralell(size_t buffer_size, SatSampBuffer* backbuffer, SatSampBuffer* frontbuffer, IQ** merged_buffer) {
		*merged_buffer = new IQ[buffer_size];
		*backbuffer = new std::map<std::string, std::pair<bool, IQ*>>;
		*frontbuffer = new std::map<std::string, std::pair<bool, IQ*>>;
	}

	void free_paralell(size_t buffer_size, SatSampBuffer backbuffer, SatSampBuffer frontbuffer, IQ* merged_buffer) {
		delete merged_buffer;
		for (auto& chanel : *backbuffer) {
			delete chanel.second.second;
		}
		delete backbuffer;
		for (auto& chanel : *frontbuffer) {
			delete chanel.second.second;
		}
		delete frontbuffer;
	}

	/// <summary>
	/// Run simulation till buffer is full
	/// </summary>
	/// <param name="buffer_size">size of buffer</param>
	/// <param name="buffer">buffer for results</param>
	void run_paralell(size_t buffer_size, SatSampBuffer buffer) {
		for (auto& sat : activeSats) {
			if (buffer->find(sat.first) == buffer->end()) {
				buffer->insert(std::make_pair(sat.first, std::make_pair(true, new IQ[buffer_size])));
			}
		}
		std::for_each(
			std::execution::par,
			activeSats.begin(),
			activeSats.end(),
			[&](std::pair<std::string, DataHandler*>&& sat)
			{
				std::string satName = sat.first;
				IQ* chanel = buffer->at(satName).second;
				if(sat.second->willBeActive() || (sampleRate/10 != buffer_size)){
					buffer->at(satName).first = true;
					for (int i = 0; i < buffer_size; i++) {
						chanel[i] = sat.second->nextSample();
					}
				}
				else {
					buffer->at(satName).first = false;
					sat.second->skipFrame();
				}
			});

	}

	/// <summary>
	/// Merge the signals generated for the diffrent satalites and send the result to the output sink
	/// </summary>
	/// <typeparam name="DST">interface to store IQ samples</typeparam>
	/// <param name="buffer_size">satalite input buffer</param>
	/// <param name="buffers">satalite input buffers</param>
	/// <param name="merged_buffer">buffer to merge data into</param>
	/// <param name="sink">output</param>
	/// <param name="numSats">sumber of satellite buffers</param>
	template<typename DST>
	void merge(size_t buffer_size, SatSampBuffer buffers, IQ* merged_buffer, DST& sink, size_t numSats) {
		for (int i = 0; i < buffer_size; i++) {
			merged_buffer[i] = 0;
		}
		for (auto& sat : *buffers) {
			if (sat.second.first) {
				for (int i = 0; i < buffer_size; i++) {
					merged_buffer[i] = merged_buffer[i] + sat.second.second[i];
				}
			}
		}
		for (int i = 0; i < buffer_size; i++) {
			IQ tmp0 = merged_buffer[i];
			IQ tmp1 = tmp0 / numSats;
			sink.add(tmp1);
		}
	}

};