#pragma once

#include <iostream>
#include <boost/asio.hpp>
#include "NetworkSink.h"
#include "Parse.h"

/*std::string read_(boost::asio::ip::tcp::socket& socket) {
	boost::asio::streambuf buf;
	boost::asio::read_until(socket, buf, "\n");
	std::string data = boost::asio::buffer_cast<const char*>(buf.data());
	return data;
}
void send_(boost::asio::ip::tcp::socket& socket, const std::string& message) {
	const std::string msg = message + "\n";
	boost::asio::write(socket, boost::asio::buffer(message));
}*/

class NetworkSource {
	boost::asio::ip::tcp::socket* socket;
	std::string read() {
		boost::asio::streambuf b;
		boost::system::error_code error;
		size_t len = boost::asio::read_until(*socket, b, "\n", error);
		if (error == boost::asio::error::eof or error.value() == 10053)
			std::cout << std::endl << "Connection Closed" << std::endl;
		else if (error) {
			throw boost::system::system_error(error); // Some other error.
		}
		std::string line((std::istreambuf_iterator<char>(&b)), std::istreambuf_iterator<char>());
		return line;
	}
	void write(const std::string& message) {
		const std::string msg = message + "\n";
		boost::system::error_code ignored_error;
		boost::asio::write(*socket, boost::asio::buffer(msg), ignored_error);
	}

public:
	NetworkSource(boost::asio::ip::tcp::socket* socket): socket(socket) {
	}
	bool getConfig(int* samplingRate, int* frequency, std::string* fileName) {
		write("config");
		std::string line = read();
		return parseConfig(line, samplingRate, frequency, fileName);
	}
	std::vector<Satellite*> getSats() {
		write("setup");
		std::string line = read();
		bool ok;
		std::vector<Satellite*> sats = parseSetup(line, &ok);
		if (!ok) {
			std::cout << "Setup parsing failed" << std::endl;
			std::cout << "'" << line << "'" << std::endl;
		}
		write("next"); // -> make shure data is ready when needed
		return sats;
	}
	std::map<std::string, DataFrame> nextData() {
		write("next");
		std::string line = read();
		bool ok;
		std::map<std::string, DataFrame> data = parseData(line, &ok);
		if (!ok) {
			std::cout << "Data parsing failed" << std::endl;
			std::cout << "'" << line << "'" << std::endl;
		}
		return data;
	}
};

void startServer() {
	using namespace boost::asio;
	using ip::tcp;
	try {
		io_context io_context;
		// listen for new connection
		tcp::acceptor acceptor(io_context, tcp::endpoint(tcp::v4(), 21978));
		for (;;) {
			//socket creation 
			tcp::socket socket(io_context);
			//waiting for connection
			std::cout << "Waiting for connection" << std::endl;
			acceptor.accept(socket); // <-- blocking
			std::cout << "Connected" << std::endl;

			NetworkSource source(&socket);

			int frequency = 0;
			int samplingRate = 0;
			std::string outputFile;
			if (source.getConfig(&samplingRate, &frequency, &outputFile)) {
				outputFile.erase(std::find_if(outputFile.rbegin(), outputFile.rend(), [](unsigned char ch) {
					return !std::isspace(ch);
					}).base(), outputFile.end());

				if (outputFile.substr(0, 6) == "tcp://") {
					std::string ipport = outputFile.substr(6);
					int split = ipport.find(":");
					std::string ip = ipport.substr(0, split);
					int port = atoi(ipport.substr(split + 1, -1).c_str());
					std::cout << "ip: " << ip << ", port: " << port << std::endl;
					NetworkSink<int8_t> sink(ip, port);
					Manager manager(samplingRate, frequency);
					std::cout << "Starting" << std::endl;
					manager.run_paralell(source, sink, 4);
					std::cout << "Done" << std::endl;
				}
				else {

					std::cout << "Output File: '" << outputFile << "'" << std::endl;
					FileSink<int8_t> fileSink(outputFile);
					Manager manager(samplingRate, frequency);
					std::cout << "Starting" << std::endl;
					manager.run_paralell(source, fileSink, 4);
					std::cout << "Done" << std::endl;
				}
			}
			else {
				std::cout << "error: first line was not configuration" << std::endl;
			}
		}
	}
	catch (std::exception& e)
	{
		std::cerr << e.what() << std::endl;
	}
}

/*
void startServer() {
	using namespace boost::asio;
	using ip::tcp;
	try {
		io_context io_context;
		// listen for new connection
		tcp::acceptor acceptor(io_context, tcp::endpoint(tcp::v4(), 21978));
		for (;;) {
			//socket creation 
			tcp::socket socket(io_context);
			//waiting for connection
			std::cout << "Waiting for connection" << std::endl;
			acceptor.accept(socket); // <-- blocking
			
			//
			//	config
			//
			std::string message = "config\n";
			boost::system::error_code ignored_error;
			boost::asio::write(socket, boost::asio::buffer(message), ignored_error);

			boost::asio::streambuf b;
			boost::system::error_code error;

			size_t len = boost::asio::read_until(socket, b, "\n", error);
			if (error == boost::asio::error::eof)
				continue; // Connection closed cleanly by peer.
			else if (error)
				throw boost::system::system_error(error); // Some other error.
			std::string config_line((std::istreambuf_iterator<char>(&b)), std::istreambuf_iterator<char>());
			std::cout << "config responce: " << std::endl << config_line;

			int samplingRate;
			int frequency;
			std::string saveFile;
			bool ok = parseConfig(config_line, &samplingRate, &frequency, &saveFile);
			if (!ok) {
				std::cout << "config failed" << std::endl;
				continue;
			}
			std::cout << "config: " << samplingRate << " " << frequency << " " << saveFile << std::endl;

			//
			//	setup
			//
			message = "setup\n";
			boost::asio::write(socket, boost::asio::buffer(message), ignored_error);

			len = boost::asio::read_until(socket, b, "\n", error);
			if (error == boost::asio::error::eof)
				continue; // Connection closed cleanly by peer.
			else if (error)
				throw boost::system::system_error(error); // Some other error.
			std::string setup_line((std::istreambuf_iterator<char>(&b)), std::istreambuf_iterator<char>());
			std::cout << "setup responce: " << std::endl << setup_line;
			std::vector<Satellite*> sats = parseSetup(setup_line, &ok);
			if (!ok) {
				std::cout << "failed to parse setup" << std::endl;
				continue;
			}
			std::cout << "Satalite Count: " << sats.size() << std::endl;

			//
			//	data
			//
			for (;;) {
				std::string message = "next\n";
				boost::system::error_code ignored_error;
				boost::asio::write(socket, boost::asio::buffer(message), ignored_error);

				boost::asio::streambuf b;
				len = boost::asio::read_until(socket, b, "\n", error);
				if (error == boost::asio::error::eof)
					break; // Connection closed cleanly by peer.
				else if (error)
					throw boost::system::system_error(error); // Some other error.
				std::string data_line((std::istreambuf_iterator<char>(&b)), std::istreambuf_iterator<char>());
				std::cout << "next responce: " << std::endl << data_line;
				std::map<std::string, DataFrame> data = parseData(data_line, &ok);
				if (!ok) {
					std::cout << "failed to parse data" << std::endl;
					break;
				}
				for (auto& kv : data) {
					std::cout << kv.first << ", ";
				}
				std::cout << "\b\b" << std::endl;
			}
		}

		//io_context.run(); // <-- async
	}
	catch (std::exception& e)
	{
		std::cerr << e.what() << std::endl;
	}
}
*/