#pragma once

#include <string>
#include <iostream>
#include <fstream>
#include <math.h>
#include "IQ.h"

template<typename T>
class FileSink {

	std::basic_ofstream<T> output;

	T buffer[512];
	int index = 0;

public:

	FileSink(std::string fileName):output(fileName, std::ios::out | std::ios::binary) {
	}

	void add(IQ iq) {
		int bitshiftmult = 1 << (sizeof(int8_t/*T*/) * 8 - 1);
		buffer[index + 0] = round(iq.I * bitshiftmult * 120 / 128 / IQ_v_unit);
		buffer[index + 1] = round(iq.Q * bitshiftmult * 120 / 128 / IQ_v_unit);

		if (iq.I > 2 * IQ_v_unit || iq.I < -2 * IQ_v_unit || iq.Q > 2 * IQ_v_unit || iq.Q < -2 * IQ_v_unit) {
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