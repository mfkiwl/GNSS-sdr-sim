#pragma once
#include <cstdint>

struct DataFrame {
  uint8_t satNum;
  uint64_t bits;
  int64_t delay;
  int32_t phaseStep;
  uint8_t power;
}; // 176 bits

