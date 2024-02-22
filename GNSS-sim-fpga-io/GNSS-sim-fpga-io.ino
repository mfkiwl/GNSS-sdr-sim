//#define DEBUG_ENABLED

#ifdef DEBUG_ENABLED
  #define DEBUG(x) Serial.print(x)
  #define DEBUGln(x) Serial.println(x)
#else
  #define DEBUG(x)
  #define DEBUGln(x)
#endif

#include "dataFrame.h"
#include "fpgaInterface.h"
#include "parsing.h"
#include "IQ.h"

const int IQPerDataFrame = sizeof(IQ)/sizeof(DataFrame);

void serialPrintIQ(IQ* samples, int n) {
  for(int i=0; i<n; i++) {
    #ifndef DEBUG_ENABLED
    Serial.write(samples[i].i);
    Serial.write(samples[i].q);
    #endif
    DEBUG((int)samples[i].i);
    DEBUG(",");
    DEBUGln((int)samples[i].q);
  }
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  FPGAInterfaceInit();

  reset();
  
  DEBUGln("waiting for input to start");
  while(Serial.available()<=0) {}
  DEBUGln("starting");
  DEBUG(sizeof(DataFrame));
  
  delay(1000);
  DEBUGln("started");
}

bool startFound = false;
void loop() {
  if(!startFound && Serial.available()>=2) {
    if (Serial.read()==0xAA) { // start bytes, 2 times 0xAA
      if (Serial.read()==0xAA) {
        startFound = true;
      } else { DEBUGln("Error 2"); }
    } else { DEBUGln("Error 1"); }
  }
  if(startFound && Serial.available()>=22) { // new data frame
    uint8_t bytes[22];
    Serial.readBytes(bytes, 22);
    DEBUGln("Frame Recieved");

    /*DataFrame frame;
    frame.satNum = bytes[0];
    frame.bits = *((uint64_t*)&bytes[1]);
    frame.delay = *((int64_t*)&bytes[9]);
    frame.phaseStep = *((int32_t*)&bytes[17]);
    frame.power = *((uint8_t*)&bytes[21]);*/

    IQ* samples = transferFrameAndIQ(bytes);
    serialPrintIQ(samples, 11);
    
    startFound = false;
  }
  else {
    IQ iq = getIQ();
    serialPrintIQ(&iq, 1);
  }
}









void loop_old() {
  // put your main code here, to run repeatedly:
  delay(1000);
  
  DEBUGln("reset FPGA");
  reset();

  int chanel = 0;
  
  DataFrame data = paramsToDataFrame(0x00000000000001aa, 64.63954998, 447.065, 250, chanel, 1602562500);
  DEBUGln("Start first Transmission");
  IQ* samples = transferFrameAndIQ(&data);
  DEBUGln("First frame Transmitted");
  serialPrintIQ(samples, IQPerDataFrame);
  DEBUGln("First samples Recieved");
  
  data = paramsToDataFrame(0x0000000000000295, 64.63952209, 447.006, 250, chanel, 1602562500);
  samples = transferFrameAndIQ(&data);
  DEBUGln("Seccond frame Transmitted");
  serialPrintIQ(samples, IQPerDataFrame);
  DEBUGln("Seccond samples Recieved");
  
  data = paramsToDataFrame(0x000000000000015a, 64.6394942, 446.947, 250, chanel, 1602562500);
  samples = transferFrameAndIQ(&data);
  DEBUGln("Third frame Transmitted");
  serialPrintIQ(samples, IQPerDataFrame);
  DEBUGln("Third samples Recieved");

  DEBUGln("starting loop");
  DEBUG("n: ");
  DEBUGln((outputRate/10-IQPerDataFrame)*3);
  for(unsigned long i=0; i<(outputRate/10-IQPerDataFrame)*3; i++) {
    IQ iq = getIQ();
    serialPrintIQ(&iq, 1);
    //if((i & ((1<<15)-1))==0) {
      //DEBUGln(i);
      //DEBUG("          ");
      //DEBUG("\r   ");
    //}
  }
  DEBUGln("loop done");
}
