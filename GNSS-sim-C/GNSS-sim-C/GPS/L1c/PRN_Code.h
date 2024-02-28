#pragma once
#include <cstdint>

#include "../../WeilCode.h"

namespace gps {
	namespace L1c {

		const uint32_t ws_p[] = {0, 5111, 5109, 5108, 5106, 5103, 5101, 5100, 5098, 5095, 5094, 5093, 5091, 5090, 5081, 5080, 5069, 5068, 5054, 5044, 5027, 5026 };
		const uint32_t ps_p[] = {0,  412,  161,    1,  303,  207, 4971, 4496,    5, 4557,  485,  253, 4676,    1,   66, 4485,  282,  193, 5211,  729, 4848,  982 };

		const uint32_t ws_d[] = {0, 5097, 5110, 5079, 4403, 4121, 5043, 5042, 5104, 4940, 5035, 4372, 5064, 5084, 5048, 4950, 5019, 5076, 3736, 4993, 5060, 5061 };
		const uint32_t ps_d[] = {0,  181,  359,   72,  110, 1480, 5034, 4622,    1, 4547,  826, 6284, 4195,  368,    1, 4796,  523,  151,  713, 9850, 5734,   34 };

		LegendreWeilCodes weil(10223);

		const uint16_t ms[] = { 0, 05111, 05421, 05501, 05403, 06417, 06141, 06351, 06501, 06205, 06235, 07751, 06623, 06733, 07627, 05667, 05051, 07665, 06325, 04365, 04745, 07633 };
		const uint16_t is[] = { 0, 03266, 02040, 01527, 03307, 03756, 03026,  0562,  0420, 03415,  0337,  0265, 01230, 02204, 01440, 02412, 03516, 02761, 03750, 02701, 01206, 01544 };

		uint8_t xorMask(uint16_t mask, uint16_t vel) {
			uint16_t x = mask & vel;
			x ^= x >> 8;
			x ^= x >> 4;
			x ^= x >> 2;
			x ^= x >> 1;
			return x & 1;
		}

		uint8_t insertedWeilCode(int n, int w, int p) {
			if      (n == p -1) {
				return 0;
			}
			else if (n == p) {
				return 1;
			}
			else if (n == p +1) {
				return 1;
			}
			else if (n == p +2) {
				return 0;
			}
			else if (n == p +3) {
				return 1;
			}
			else if (n == p +4) {
				return 0;
			}
			else if (n == p +5) {
				return 0;
			}
			else {
				return weil.weilCode(n, w);
			}
		}

		class PRN {

			uint32_t w_p, p_p, w_d, p_d;

			int n;

			uint16_t regS1;
			uint16_t regS2;

			uint16_t m;
			uint16_t init;

		public:
			PRN(int prn) {
				w_p = ws_p[prn];
				p_p = ps_p[prn];
				w_d = ws_d[prn];
				p_d = ps_d[prn];
				m   =   ms[prn];
				init =  is[prn];
				reset();
				resetOverlay();
			}

			void reset() {
				n = 0;
			}

			void resetOverlay() {
				regS1 = init<<1;
				regS2 = 0b00000000000<<1;
			}

			uint8_t nextOverlay() {
				uint8_t s1 = xorMask(m, regS1);
				regS1 |= s1;
				uint8_t s2 = xorMask(1 << 11 | 1 << 9, regS2);
				regS2 |= s2;

				uint8_t v1 = (regS1 >> 11) & 1;
				uint8_t v2 = (regS2 >> 11) & 1;
				uint8_t v = (v1 ^ v2);

				regS1 = regS1 << 1;
				regS2 = regS2 << 1;

				return v;
			}

			uint8_t next() { // data and pilot

				uint8_t pilot = insertedWeilCode(n, w_p, p_p); // BOC(1, 1)
				uint8_t data  = insertedWeilCode(n, w_d, p_d); // TMBOC() / BOC(1, 1) + BOC(1, 6)

				n++;
				return pilot << 1 | data;
			}


		};

	}
}