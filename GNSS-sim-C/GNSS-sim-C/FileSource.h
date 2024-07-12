#pragma once

#include <iostream>
#include <string>
#include <sstream>
#include <fstream>
#include <vector>
#include <map>
#include <stdexcept>

#include "Satellite.h"
#include "DataFrame.h"

#include "Parse.h"

/*#include "Galileo/Sat.h"
#include "Glonass/Sat.h"
#include "GPS/Sat.h"
#include "BeiDou/Sat.h"
#include "IRNSS/Sat.h"

Satellite* constructSat(std::string constelationCode, std::string id, std::string arg) {
	//std::cout << constelationCode << " " << id << " " << arg << std::endl;
	if (constelationCode == "E") {
		Satellite* sat = new galileo::Sat(std::stoi(id));
		return sat;
	}
	if (constelationCode == "R") {
		Satellite* sat = new glonass::Sat(std::stoi(id), std::stoi(arg));
		return sat;
	}
	if (constelationCode == "G") {
		Satellite* sat = new gps::Sat(std::stoi(id));
		return sat;
	}
	if (constelationCode == "C") {
		Satellite* sat = new beidou::Sat(std::stoi(id));
		return sat;
	}
	if (constelationCode == "I") {
		Satellite* sat = new irnss::Sat(std::stoi(id));
		return sat;
	}
	throw std::invalid_argument("Unexpeced constelation code");
}*/

class FileSource {
	std::ifstream file;
public:
	FileSource(std::string fileName) {

		file.open(fileName);
		

	}

	bool getConfig(int* samplingRate, int* frequency, std::string* fileName) {
		if (file.is_open()) {
			std::string line;
			std::streampos oldpos = file.tellg();
			while (std::getline(file, line))
			{

				if (line.rfind("config") == 0) {
					
					std::string config_string = line.substr(7);
					int split = config_string.find(" ");
					*frequency = std::stoi(config_string.substr(0, split));
					config_string = config_string.substr(split + 1);
					split = config_string.find(" ");
					if (split >= 0) {
						*fileName = config_string.substr(split + 1);
					}
					*samplingRate = std::stoi(config_string.substr(0, split));

					//file.seekg(oldpos);
					return true;
				}
				if (line.rfind("setup") == 0 || line.rfind("data") == 0) {

					file.seekg(oldpos);
					return false;
				}
			}
			throw std::invalid_argument("File does not contain setup data");
		}
		throw std::invalid_argument("File not open");
	}

	std::vector<Satellite*> getSats() {
		if (file.is_open()) {
			std::string line;
			while (std::getline(file, line))
			{
				if (line.rfind("setup") == 0) {
					//std::cout << line << std::endl;
					std::vector<Satellite*> sats;

					std::string constelations = line.substr(6);
					//std::cout << "'" << constelations << "'" << std::endl;

					std::stringstream constelations_ss(constelations);
					std::string constelation;
					while (std::getline(constelations_ss, constelation, ' ')) {
						int pos = constelation.rfind(":");
						std::string name = constelation.substr(0, pos);
						std::string data = constelation.substr(pos + 2, constelation.length()-pos-3);
						//std::cout << "  name: '"<< name << "' data: '"<< data << "'" << std::endl;

						std::stringstream data_ss(data);
						std::string satinfo;
						while (std::getline(data_ss, satinfo, ',')) {
							int open = satinfo.find('[');
							int close = satinfo.find(']');
							std::string satId = satinfo.substr(0, open);
							std::string satArg = satinfo.substr(open+1, close-open-1);

							//std::cout << "    id: '" << satId << "' arg:'" << satArg << "'" << std::endl;

							sats.push_back(constructSat(name, satId, satArg));
						}
					}

					return sats;
				}
			}
			throw std::invalid_argument("File does not contain setup data");
		}
		throw std::invalid_argument("File not open");
	}

	std::map<std::string, DataFrame> nextData() {
		if (file.is_open()) {
			std::map<std::string, DataFrame> map;
			std::string line;
			while (std::getline(file, line))
			{
				if (line.rfind("data") == 0) {

					//std::cout << line << std::endl;

					std::string entries = line.substr(5);
					std::stringstream entries_ss(entries);
					std::string entry;
					while (std::getline(entries_ss, entry, ',')) {
						int split_id = entry.find(":");
						// hex data
						int split_data_1 = entry.find("_");
						// delay
						int split_data_2 = entry.find("_", split_data_1 + 1);
						// shift
						int split_data_3 = entry.find("_", split_data_2 + 1);
						// power
						int split_data_4 = entry.find("_", split_data_3 + 1);
						int split_data_5 = -1;
						int split_data_6 = -1;
						int end = entry.length();
						float dx = 0, dy = 0, dz = 0;
						if (split_data_4 == std::string::npos) {
							split_data_4 = end;
						}
						else {
							// dx
							int split_data_5 = entry.find("_", split_data_4 + 1);
							// dy
							int split_data_6 = entry.find("_", split_data_5 + 1);
							// dz

							if (split_data_5 != std::string::npos && split_data_6 != std::string::npos) {
								dx = std::stof(entry.substr(split_data_4 + 1, split_data_5 - split_data_4));
								dy = std::stof(entry.substr(split_data_5 + 1, split_data_6 - split_data_5));
								dz = std::stof(entry.substr(split_data_6 + 1, end          - split_data_6));
							}
						}

						std::string name = entry.substr(0, split_id);
						std::string dataHex = entry.substr(split_id+1, split_data_1 - split_id-1);
						std::string delayS = entry.substr(split_data_1+1, split_data_2 - split_data_1-1);
						std::string shiftS = entry.substr(split_data_2+1, split_data_3 - split_data_2-1);
						std::string powerS = entry.substr(split_data_3+1, split_data_4 - split_data_3);

						unsigned long long data = std::stoull(dataHex, nullptr, 16);
						double delay = std::stod(delayS);
						double shift = std::stod(shiftS);
						int power = std::stoi(powerS);

						//std::cout << "'" << name << "' '" << dataHex << "' '" << delayS << "' '" << shiftS << "' '" << powerS << "'" << std::endl;
						//std::cout << "'" << data << "' '" << delay << "' '" << shift << "' '" << power << "'" << std::endl;

						DataFrame frame;
						frame.bits = data;
						frame.delay = delay;
						frame.doppler = shift;
						frame.power = power;
						frame.dx = dx;
						frame.dy = dy;
						frame.dz = dz;

						map[name] = frame;
					}

					return map;
				}
			}
			file.close();
			return map;
		}
		throw std::invalid_argument("File not open");
	}
};