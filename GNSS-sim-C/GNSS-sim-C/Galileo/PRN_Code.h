#pragma once

#include <string>
#include <iostream>
#include <fstream>
#include <bitset>
#include <unordered_map>
#include <stdexcept>


namespace galileo {

	const size_t code_length = 4092;
	typedef std::bitset<code_length> Prn;

	const char* SC25_hex = "380AD90";
	uint8_t SC25_uint8[] = { 0,0,1,1, 1,0,0,0, 0,0,0,0, 1,0,1,0, 1,1,0,1, 1,0,0,1, 0 };
	const size_t SC25_length = 25;
	unsigned long CS25_num = 0;// 0x380AD90 >> 3;

	std::bitset<25> getSC25() {
		std::bitset<25> bits_reverse(CS25_num);

		std::bitset<25> bits;
		for (int i = 0; i < 25; i++) {
			bits.set(i, bits_reverse.test(24 - i));
		}

		return bits;
	}

	Prn setBits(char* code) {
		std::bitset<code_length> bits;
		for (int i = 0; i < code_length / 4; i++) {
			int n = code[i] - '0';
			if (n < 0 || n>9) {
				//n = code[i] - 'F' + 10;
				n = code[i] - 'A' + 10;
			}
			if (n < 0 || n>15) {
				std::cout << "invalid char" << std::endl;
			}
			bits.set(i * 4 + 0, (n & 0b1000) != 0);
			bits.set(i * 4 + 1, (n & 0b0100) != 0);
			bits.set(i * 4 + 2, (n & 0b0010) != 0);
			bits.set(i * 4 + 3, (n & 0b0001) != 0);
		}
		return bits;
	}

	std::unordered_map<std::string, Prn> getPRNCodes(std::string file_name) {
		std::unordered_map<std::string, std::bitset<code_length>> all;
		std::basic_ifstream<char> file(file_name, std::ios::in);
		if (file.is_open()) {

			const size_t name_size = 32;
			char name[name_size];

			char delimiter;

			const size_t code_char_size = 1050;
			char code_chars[code_char_size];

			while (!file.eof() && file.peek() != std::char_traits<char>::eof()) {
				file.getline(name, name_size, ';');
				//std::cout << "name: '" << name << "'" << std::endl;

				file.getline(code_chars, code_char_size);
				//std::cout << "code: '" << code_chars << "'" << std::endl;

				std::bitset<code_length> prn = setBits(code_chars);

				//for (int i = 0; i < code_length; i++) {
				//	std::cout << prn.test(i);
				//}
				//std::cout << std::endl;

				all.insert({ std::string(name), prn });

			}

			file.close();
			return all;
		}
		else {
			std::cout << "could not open file" << std::endl;
			throw std::invalid_argument("could not open file");

		}
	}

}