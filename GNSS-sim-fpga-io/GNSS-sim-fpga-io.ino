#include "dataFrame.h"
#include "fpgaInterface.h"
#include "parsing.h"
#include "IQ.h"

const int IQPerDataFrame = sizeof(IQ)/sizeof(DataFrame);

void serialPrintIQ(IQ* samples, int n) {
  for(int i=0; i<n; i++) {
    Serial.print((int)samples[i].i);
    Serial.print(",");
    Serial.println((int)samples[i].q);
  }
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  FPGAInterfaceInit();
  
  Serial.println("waiting for input to start");
  while(Serial.available()<=0) {}
  Serial.println("starting");
  
  delay(1000);
  Serial.println("started");
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(1000);
  
  Serial.println("reset FPGA");
  reset();

  DataFrame data = paramsToDataFrame(0x00000000000001aa, 64.63954998, 447.065, 250, 0, 1602562500);
  Serial.println("Start first Transmission");
  IQ* samples = transferFrameAndIQ(&data);
  Serial.println("First frame Transmitted");
  serialPrintIQ(samples, IQPerDataFrame);
  Serial.println("First samples Recieved");
  
  data = paramsToDataFrame(0x0000000000000295, 64.63952209, 447.006, 250, 0, 1602562500);
  samples = transferFrameAndIQ(&data);
  Serial.println("Seccond frame Transmitted");
  serialPrintIQ(samples, IQPerDataFrame);
  Serial.println("Seccond samples Recieved");
  
  data = paramsToDataFrame(0x000000000000015a, 64.6394942, 446.947, 250, 0, 1602562500);
  samples = transferFrameAndIQ(&data);
  Serial.println("Third frame Transmitted");
  serialPrintIQ(samples, IQPerDataFrame);
  Serial.println("Third samples Recieved");

  Serial.println("starting loop");
  Serial.print("n: ");
  Serial.println((outputRate/10-IQPerDataFrame)*3);
  for(unsigned long i=0; i<(outputRate/10-IQPerDataFrame)*3; i++) {
    IQ iq = getIQ();
    serialPrintIQ(&iq, 1);
    //if((i & ((1<<15)-1))==0) {
    //  Serial.print(i);
    //  Serial.print("          ");
    //  Serial.print("\r   ");
    //}
  }
  Serial.println("loop done");
}
