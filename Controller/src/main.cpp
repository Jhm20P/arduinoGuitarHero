#include <Arduino.h>
#include <SPI.h>
#include <Arduino_MKRIoTCarrier.h>
#include <websockets/websocket.hpp>


void setup() {


  Serial.begin(9600);

  while (!Serial) {
    ;  // wait for serial port to connect. Needed for native USB port only
    
  }

  Serial.println();
  Serial.println();
  Serial.println();

  websocket::webSocketWIFI();
  
}

void loop() {
  websocket::webSocketLoop();
}