#pragma once

#include <string>
#include <iostream>
#include <fstream>
#include <math.h>
#include "IQ.h"

class FileSink {

	std::basic_ofstream<int8_t> output;

	int8_t buffer[512];
	int index = 0;

public:

	FileSink(std::string fileName):output(fileName, std::ios::out | std::ios::binary) {
	}

	void add(IQ iq) {
		buffer[index + 0] = round(iq.I * 120);
		buffer[index + 1] = round(iq.Q * 120);

		if (iq.I > 2 || iq.I < -2 || iq.Q > 2 || iq.Q < -2) {
			std::cout << "overflow" << std::endl;
		}

		if (buffer[index + 0] == 1 || buffer[index + 0] == -1) { // weard behavier in iq engine, iq flip around if this is not in place
			buffer[index + 0] *= 2;
		}
		if (buffer[index + 1] == 1 || buffer[index + 1] == -1) { // weard behavier in iq engine, iq flip around if this is not in place
			buffer[index + 1] *= 2;
		}

		index += 2;
		if (index >= 512) {
			output.write(buffer, 512);
			index = 0;
		}
	}

	void close() {
		if (index > 0) {
			output.write(buffer, index);
		}
		output.close();
	}
};