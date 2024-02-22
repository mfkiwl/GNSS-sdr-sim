#pragma once

struct DataFrame {
  uint8_t satNum;
  uint64_t bits;
  int64_t delay;
  int32_t phaseStep;
  uint8_t power;
};

unsigned long radioFrequencyOut = 1602000000;
unsigned long outputRate = 15000000;
unsigned long modulationRate = 511000;
int subCycles = 100;

DataFrame paramsToDataFrame(uint64_t bits, double delay, float doppler, int power, int prn, unsigned long radioFrequencyIn) {
  
  double delay_samples = delay / 1000 * outputRate;
  uint64_t delay_n = (subCycles * modulationRate) * delay_samples;

  int PHASE_POWER = 30;
  unsigned long PHASE_RANGE = 1<<PHASE_POWER; // 2 ^ 30

  int scale = 100;
  unsigned long targetFrequency = radioFrequencyIn*scale + doppler*scale;
  long shift = targetFrequency - radioFrequencyOut * scale;
  double normalPhaseSampleDelta = shift / (double)outputRate;
  uint32_t unitStepPhase = normalPhaseSampleDelta / scale * (PHASE_RANGE);

  DataFrame data;
  data.satNum = prn;
  data.bits = bits;
  data.delay = delay_n;
  data.phaseStep = unitStepPhase;
  data.power = power;

  return data;
}
