#include <Arduino.h>
#include <SPI.h>
#include <Arduino_MKRIoTCarrier.h>
#include <websockets/websocket.hpp>
#include <states/StateManager.hpp>
#include <states/MenuState.hpp>
#include <websockets/ServerInfo.hpp>

MKRIoTCarrier carrier;
StateManager stateManager(&carrier);

void setup() {
  carrier.begin();
  carrier.display.init(240, 240);
  carrier.display.setTextSize(1);
  carrier.Buttons.begin();

  websocket::registerStateManager(&stateManager);

  Serial.begin(9600);

  while (!Serial) {
    ;  // wait for serial port to connect. Needed for native USB port only
    
  }

  Serial.println();
  Serial.println();
  Serial.println();

  websocket::webSocketWIFI();
  


  stateManager.setState("MenuState");

  Serial.println("Setup complete");
}

void loop() {
  carrier.Buttons.update();
  websocket::webSocketLoop();
  stateManager.loop();
}