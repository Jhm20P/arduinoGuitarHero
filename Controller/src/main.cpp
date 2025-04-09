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

  

  websocket::registerStateManager(&stateManager);

  Serial.begin(9600);

  while (!Serial) {
    ;  // wait for serial port to connect. Needed for native USB port only
    
  }

  Serial.println();
  Serial.println();
  Serial.println();

  websocket::webSocketWIFI();
  


  stateManager.setState("MenuState"); // Set the initial state to PlayingState

  Serial.println("Setup complete");
}

void loop() {
  carrier.Buttons.update(); // Update the touch buttons state

  // Debugging: Check button states
  if (carrier.Buttons.onTouchDown(TOUCH1)) {
    Serial.println("TOUCH1 pressed");
  }
  if (carrier.Buttons.onTouchDown(TOUCH0)) {
    Serial.println("TOUCH0 pressed");
  }
  if (carrier.Buttons.onTouchDown(TOUCH2)) {
    Serial.println("TOUCH2 pressed");
  }

  websocket::webSocketLoop();
  // Serial.println(rand() % 1000 + 1);
  stateManager.loop();
  delay(30);
}