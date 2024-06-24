#pragma once
#include <stdint.h>
#include <iostream>
#define _USE_MATH_DEFINES
#include <math.h>
#include <type_traits>

//#define IQ_FLOATS

#ifdef IQ_FLOATS
typedef double IQ_v;
const double IQ_v_unit = 1.0;
#else
typedef int IQ_v;
const int IQ_v_unit = 512;
#endif




const size_t TRIG_TABLE_SIZE = 256;
const int SIN_TABLE[256] = {
	  0,   1,   3,   4,   6,   7,   9,  10,  12,  14,  15,  17,  18,  20,  21,  23,
	 24,  26,  28,  29,  31,  32,  34,  35,  37,  38,  40,  42,  43,  45,  46,  48,
	 49,  51,  52,  54,  55,  57,  58,  60,  61,  63,  64,  66,  68,  69,  71,  72,
	 74,  75,  77,  78,  79,  81,  82,  84,  85,  87,  88,  90,  91,  93,  94,  96,
	 97,  99, 100, 101, 103, 104, 106, 107, 109, 110, 111, 113, 114, 116, 117, 118,
	120, 121, 122, 124, 125, 127, 128, 129, 131, 132, 133, 135, 136, 137, 139, 140,
	141, 142, 144, 145, 146, 148, 149, 150, 151, 153, 154, 155, 156, 158, 159, 160,
	161, 162, 164, 165, 166, 167, 168, 170, 171, 172, 173, 174, 175, 176, 178, 179,
	180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 191, 192, 193, 194, 195, 196,
	197, 198, 199, 200, 201, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211,
	212, 212, 213, 214, 215, 216, 217, 217, 218, 219, 220, 221, 221, 222, 223, 224,
	224, 225, 226, 227, 227, 228, 229, 229, 230, 231, 231, 232, 233, 233, 234, 234,
	235, 236, 236, 237, 237, 238, 239, 239, 240, 240, 241, 241, 242, 242, 243, 243,
	244, 244, 244, 245, 245, 246, 246, 246, 247, 247, 248, 248, 248, 249, 249, 249,
	250, 250, 250, 250, 251, 251, 251, 252, 252, 252, 252, 252, 253, 253, 253, 253,
	253, 253, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254, 254
};

struct IQ {
	IQ_v I;
	IQ_v Q;

	IQ(IQ_v I, IQ_v Q) : I(I), Q(Q) {}
	IQ(IQ_v I           ) : I(I), Q(0) {}
	IQ() : I(0), Q(0) {}

	IQ rotate(double phase) {
		//std::cout << phase << " : " << cos(phase) << ", " << sin(phase) << " @ (" << I << ", " << Q << ")" << std::endl;
		return IQ(
			cos(phase) * I + sin(phase) * Q,
			sin(phase) * I - cos(phase) * Q
		);
	}

	IQ rotate(long phase) {
		int tableIndex = (phase >> 20) & 0b11111111;
		int tableOp = (phase >> 28) & 0b11;
		int sinPhase;
		int cosPhase;
		switch (tableOp) {
		case 0b00:
			sinPhase =  SIN_TABLE[tableIndex];
			cosPhase =  SIN_TABLE[TRIG_TABLE_SIZE - 1 - tableIndex];
			break;
		case 0b01:
			sinPhase =  SIN_TABLE[TRIG_TABLE_SIZE - 1 - tableIndex];
			cosPhase = -SIN_TABLE[tableIndex];
			break;
		case 0b10:
			sinPhase = -SIN_TABLE[tableIndex];
			cosPhase = -SIN_TABLE[TRIG_TABLE_SIZE - 1 - tableIndex];
			break;
		case 0b11:
			sinPhase = -SIN_TABLE[TRIG_TABLE_SIZE - 1 - tableIndex];
			cosPhase =  SIN_TABLE[tableIndex];
			break;
		}

		return IQ(
			(cosPhase * I + sinPhase * Q)/256, 
			(sinPhase * I - cosPhase * Q)/256
		);
	}

	IQ operator+(IQ const& obj) {
		IQ res(I + obj.I, Q + obj.Q);
		return res;
	}

	template <typename NumericType>
	IQ operator/(NumericType num) {
		static_assert(std::is_arithmetic<NumericType>::value, "NumericType must be numeric");
		IQ_v In = I / (IQ_v)num;
		IQ_v Qn = Q / (IQ_v)num;
		IQ res(In, Qn);
		return res;
	}

	template <typename NumericType>
	IQ operator*(NumericType num) {
		static_assert(std::is_arithmetic<NumericType>::value, "NumericType must be numeric");
		IQ res(I * num, Q * num);
		return res;
	}
};

std::ostream& operator<<(std::ostream& os, const IQ& iq)
{
	os << "(" << iq.I << ", " << iq.Q << ")";
	return os;
}
