#pragma once
#include <stdint.h>
#include <iostream>
#define _USE_MATH_DEFINES
#include <math.h>
#include <type_traits>

struct IQ {
	double I;
	double Q;

	IQ(double I, double Q) : I(I), Q(Q) {}
	IQ(double I           ) : I(I), Q(0) {}
	IQ() : I(0), Q(0) {}

	IQ rotate(double phase) {
		//std::cout << phase << " : " << cos(phase) << ", " << sin(phase) << " @ (" << I << ", " << Q << ")" << std::endl;
		return IQ(
			cos(phase) * I + sin(phase) * Q,
			sin(phase) * I + cos(phase) * Q
		);
	}

	IQ operator+(IQ const& obj) {
		IQ res(I + obj.I, Q + obj.Q);
		return res;
	}

	template <typename NumericType>
	IQ operator/(NumericType num) {
		static_assert(std::is_arithmetic<NumericType>::value, "NumericType must be numeric");
		IQ res(I/num, Q/num);
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
