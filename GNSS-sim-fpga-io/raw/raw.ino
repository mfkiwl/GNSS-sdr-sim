//#define DEBUG_ENABLED

#ifdef DEBUG_ENABLED
  #define DEBUG(x) Serial.print(x)
  #define DEBUGln(x) Serial.println(x)
#else
  #define DEBUG(x)
  #define DEBUGln(x)
#endif


#include "iq.h"
#include "fpgaInterface.h"

void setup() {
  Serial.begin(115200);

  FPGAInterfaceInit();

  reset();
  
  DEBUGln("waiting for input to start");
  while(Serial.available()<=0) {}
  DEBUGln("starting");
  
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

    for(int i=0; i<22; i++) {
      DEBUG((int)bytes[i]);
      DEBUG("-");
    }
    DEBUGln("");
    
    IQ* samples = transferFrameAndIQ(bytes, 22);
    serialPrintIQ(samples, 11);
    
    startFound = false;
  }
  else {
    IQ iq = getIQ();
    serialPrintIQ(&iq, 1);
  }
}
