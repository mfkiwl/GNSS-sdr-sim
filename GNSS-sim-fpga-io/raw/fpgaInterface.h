#pragma once

#include <SPI.h>

#include "iq.h"

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
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);
  delayMicroseconds(1);
  digitalWrite(resetPin, HIGH);
  delayMicroseconds(1);

  digitalWrite(13, HIGH);
  delayMicroseconds(1);
  digitalWrite(13, LOW);
  delayMicroseconds(1);
  
  digitalWrite(resetPin, LOW);
  delayMicroseconds(1);
  SPI.begin();
}

void store() {
  delayMicroseconds(1);
  digitalWrite(storePin, HIGH);
  delayMicroseconds(1);
  digitalWrite(storePin, LOW);
  delayMicroseconds(1);
}

//#define SPI_SETTINGS SPISettings(16000000, MSBFIRST, SPI_MODE0)

#define SPI_SETTINGS SPISettings(1600000, MSBFIRST, SPI_MODE0)


IQ* transferFrameAndIQ(uint8_t* frame, size_t bytes) {

  // select a signal that we are sending data
  SPI.beginTransaction(SPI_SETTINGS);
  SPI.transfer(frame, bytes);
  SPI.endTransaction();
  // deselct when do to get the data to the right place
  store();
  // assume we are always getting data back
  return (IQ*)frame;

}

IQ getIQ() {
  IQ iq = new_IQ(0b10101010, 0b10101010);
  SPI.beginTransaction(SPI_SETTINGS);
  SPI.transfer(&iq, sizeof(iq));
  SPI.endTransaction();
  return iq;
}
