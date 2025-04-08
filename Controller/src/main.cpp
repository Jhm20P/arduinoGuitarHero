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

  websocket::registerStateManager(&stateManager);

  Serial.begin(9600);

  while (!Serial) {
    ;  // wait for serial port to connect. Needed for native USB port only
    
  }

  Serial.println();
  Serial.println();
  Serial.println();

  websocket::webSocketWIFI();
  


  //stateManager.setState("MenuState");

  ServerInfo *servers = websocket::getServers();
  if (servers == nullptr) {
    Serial.println("No servers found.");
  }
  else {
    Serial.println("Servers found:");
    for (int i = 0; i < 10; i++) {
      if (servers[i].ipaddress == nullptr) {
        break; // Stop if we reach an empty server entry
      }
      Serial.print("Server IP: ");
      Serial.println(servers[i].ipaddress);
      Serial.print("Server Port: ");
      Serial.println(servers[i].port);
      Serial.print("Host Name: ");
      Serial.println(servers[i].HostName);
      Serial.print("Game Name: ");
      Serial.println(servers[i].GameName);
    }
  }
}

void loop() {
  //websocket::webSocketLoop();
  //stateManager.loop();
}