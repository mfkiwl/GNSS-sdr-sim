#pragma once

#include <string>
#include <iostream>
#include <fstream>
#include <memory>
#include <algorithm>
#include <thread>
#include <chrono>
#include <math.h>
#include <boost/asio.hpp>
#include "IQ.h"

/// <summary>
/// Send IQ samples out over the network
/// </summary>
/// <typeparam name="T">type of data to output: int8_t or int16_t</typeparam>
template<typename T>
class NetworkSink {

	#define packetSize 2048

	boost::asio::io_service service;
	//std::unique_ptr<boost::asio::ip::tcp::socket> socket;
	boost::asio::ip::tcp::socket socket;


	T buffer[packetSize];
	int index = 0;

public:

	NetworkSink(std::string ip, int port): socket(service) {
		
		using namespace boost::asio::ip;

		//tcp::socket socket(service);
		tcp::endpoint endpoint(address::from_string(ip), port);
		
		std::cout << "[Client] Connecting to server..." << std::endl;
		socket.connect(endpoint);
		std::cout << "[Client] Connection successful" << std::endl;

		
	}

	void add(IQ iq) {
		int bitshiftmult = 1 << (sizeof(T) * 8 - 1);
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
		if (index >= packetSize) {
			if (socket.available()>0) {
				//std::cout << "pause" << std::endl;
				char data[64] = {0};
				boost::asio::read(socket, boost::asio::buffer(data, std::min(63, (int)socket.available())));

				using namespace std::chrono_literals;
				std::this_thread::sleep_for(10ms);
				//std::cout << "from GNU Radio: " << data << std::endl;
			}
			boost::system::error_code ignored_error;
			boost::asio::write(socket, boost::asio::buffer((void*)buffer, sizeof(T)*packetSize), ignored_error);
			//output.write(buffer, packetSize);
			index = 0;
		}
	}

	void close() {
		if (index > 0) {
			boost::system::error_code ignored_error;
			boost::asio::write(socket, boost::asio::buffer((void*)buffer, sizeof(T) * index), ignored_error);
		}
		socket.close();
	}
};