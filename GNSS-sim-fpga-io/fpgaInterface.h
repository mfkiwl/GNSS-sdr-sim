#pragma once

#include <SPI.h>

#include "dataFrame.h"
#include "IQ.h"

IQ* transferFrameAndIQ(DataFrame* frame) {

  // select a signal that we are sending data
  SPI.transfer(frame, sizeof(DataFrame));
  // deselct when do to get the data to the right place

  // assume we are always getting data back
  return (IQ*)frame;

}

IQ getIQ() {
  IQ iq;
  SPI.transfer(&iq, sizeof(iq));
  return iq;
}

