#pragma once

#include <SPI.h>

#include "dataFrame.h"
#include "IQ.h"

uint8_t resetPin = 9;
uint8_t storePin = 10;

void FPGAInterfaceInit() {
  pinMode(resetPin, OUTPUT);
  digitalWrite(resetPin, HIGH);

  pinMode(storePin, OUTPUT);
  digitalWrite(storePin, LOW);

  SPI.beginTransaction(SPISettings(16000000, MSBFIRST, SPI_MODE0));
}

void FPGAInterfaceClose() {
  SPI.endTransaction();
}

void reset() {
  digitalWrite(resetPin, HIGH);
  delayMicroseconds(1);
  digitalWrite(resetPin, LOW);
  delayMicroseconds(1);
}

void store() {
  delayMicroseconds(1);
  digitalWrite(storePin, HIGH);
  delayMicroseconds(1);
  digitalWrite(storePin, LOW);
  delayMicroseconds(1);
}

IQ* transferFrameAndIQ(DataFrame* frame) {

  // select a signal that we are sending data
  SPI.transfer(frame, sizeof(DataFrame));
  // deselct when do to get the data to the right place
  store();
  // assume we are always getting data back
  return (IQ*)frame;

}

IQ getIQ() {
  IQ iq;
  SPI.transfer(&iq, sizeof(iq));
  return iq;
}


