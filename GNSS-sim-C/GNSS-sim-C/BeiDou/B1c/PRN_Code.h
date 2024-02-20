#pragma once

#include "../../WeilCode.h"

namespace beidou { namespace B1c {

	LegendreWeilCodes primery(10243);
	LegendreWeilCodes secondary(3607);

	class PRN {
	private:
		int w_data_prim;
		int p_data_prim;
		int w_pilot_prim;
		int p_pilot_prim;

		//int w_data_sec;
		//int p_data_sec;
		int w_pilot_sec;
		int p_pilot_sec;
	public:
		PRN(int w_data_prim, int p_data_prim, int w_pilot_prim, int p_pilot_prim, int w_pilot_sec, int p_pilot_sec) :
			w_data_prim(w_data_prim), p_data_prim(p_data_prim), w_pilot_prim(w_pilot_prim), p_pilot_prim(p_pilot_prim), w_pilot_sec(w_pilot_sec), p_pilot_sec(p_pilot_sec) {}

		uint8_t getData(int n, int n_sec) {
			return primery.truncatedWeilCode(n, w_data_prim, p_data_prim);
		}

		uint8_t getPilot(int n, int n_sec) {
			return primery.truncatedWeilCode(n, w_pilot_prim, p_pilot_prim) ^ secondary.truncatedWeilCode(n_sec, w_pilot_sec, p_pilot_sec);
		}
	};
}}