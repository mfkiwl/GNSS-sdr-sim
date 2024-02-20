#pragma once
#include <cstdint>
#include <algorithm>

class LegendreWeilCodes {
	size_t N;
	uint8_t* legendre;

	void genLegendre() {
		legendre[0] = 0;
		for (int k = 1; k < N; k++) {
			legendre[k] = 0;
			for (int x = 0; x < N; x++) {
				if ((x * x) % N == k) {
					legendre[k] = 1;
					break;
				}
			}
		}
	}

public:
	LegendreWeilCodes(size_t N) : N(N) {
		legendre = new uint8_t[N];
		genLegendre();
	}

	~LegendreWeilCodes() {
		delete legendre;
	}

	LegendreWeilCodes(const LegendreWeilCodes& other) : N(other.N), legendre(other.legendre) {}
	LegendreWeilCodes& operator=(const LegendreWeilCodes& other) {
		delete legendre;
		N = other.N;
		legendre = new uint8_t[N];
		std::copy(other.legendre, other.legendre+other.N, legendre);
	}

	uint8_t weilCode(int k, int w) {
		return legendre[k] ^ legendre[(k + w) % N];
	}

	uint8_t truncatedWeilCode(int n, int w, int p) {
		return weilCode((n + p - 1) % N, w);
	}
};