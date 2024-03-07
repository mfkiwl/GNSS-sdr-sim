#pragma once

typedef uint16_t IQ;

int8_t IQ_i(IQ iq) {
  IQ* ref = &iq;
  int8_t* split = (int8_t*)ref;
  return split[0];
  //return 0;
}
int8_t IQ_q(IQ iq) {
  IQ* ref = &iq;
  int8_t* split = (int8_t*)ref;
  return split[1];
  //return 0;
  //return ((*int8_t)&iq)[1];
}

IQ new_IQ(int8_t i, int8_t q) {
  uint16_t v = 0;
  uint16_t* ref = &v;
  int8_t* split = (int8_t*)ref;
  split[0] = i;
  split[1] = q;
  return v;
}

void serialPrintIQ(IQ* samples, int n) {
  for(int i=0; i<n; i++) {
    #ifndef DEBUG_ENABLED
    //Serial.write(IQ_i(samples[i]));
    //Serial.write(IQ_q(samples[i]));
    Serial.write(samples, n*2);
    #endif
    DEBUG((int)IQ_i(samples[i]));
    DEBUG(",");
    DEBUGln((int)IQ_q(samples[i]));
  }
}
