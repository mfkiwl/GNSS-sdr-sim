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

  //SPI.beginTransaction(SPISettings(16000000, MSBFIRST, SPI_MODE0));
  SPI.begin();
}

void FPGAInterfaceClose() {
  //SPI.endTransaction();
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

//#define SPI_SETTINGS SPISettings(16000000, MSBFIRST, SPI_MODE0)

#define SPI_SETTINGS SPISettings(160000, MSBFIRST, SPI_MODE0)

IQ* transferFrameAndIQ(DataFrame* frame) {

  // select a signal that we are sending data
  SPI.beginTransaction(SPI_SETTINGS);
  SPI.transfer(&frame->satNum, 1);
  SPI.transfer(&frame->bits, 8);
  SPI.transfer(&frame->delay, 8);
  SPI.transfer(&frame->phaseStep, 4);
  SPI.transfer(&frame->power, 1);
  SPI.endTransaction();
  // deselct when do to get the data to the right place
  store();
  // assume we are always getting data back
  return (IQ*)frame;

}

IQ getIQ() {
  IQ iq;
  iq.i=0b10101010;
  iq.q=0b10101010;
  SPI.beginTransaction(SPI_SETTINGS);
  SPI.transfer(&iq, sizeof(iq));
  SPI.endTransaction();
  return iq;
}
