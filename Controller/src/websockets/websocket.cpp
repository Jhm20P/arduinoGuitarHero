#include <Arduino.h>
#include <SPI.h>
#include <config.hpp>
#include "websocket.hpp"
#include "ServerInfo.hpp"
#define _ssid WIFI_SSID
#define _pass WIFI_PASSWORD

#define SSID _ssid
#define PASS _pass

StateManager* websocket::_stateManager = nullptr;
WiFiClient websocket::client;
WebSocketsClient websocket::webSocket;
     

int status = WL_IDLE_STATUS;


void websocket::webSocketSend(char message[]) {
    if (webSocket.isConnected()) {
      webSocket.sendTXT(message);
    } else {
        Serial.println("WebSocket not connected. Cannot send message.");
    }
}

void websocket::webSocketEvent(WStype_t type, uint8_t *payload, size_t length) {
    switch (type) {
        case WStype_DISCONNECTED:
          Serial.println("[WSc] Disconnected!");
          break;
        case WStype_CONNECTED:
          Serial.println("[WSc] Connected!");
    
          // send message to server when Connected
          webSocket.sendTXT("Connected");
          break;
        case WStype_TEXT:
          Serial.print("[WSc] get text:");
          Serial.println((char *)payload);

          // If payload starts with "SM-", it indicates a state change
          if (strncmp((char *)payload, "SM-", 3) == 0) {
            // Extract the state name from the payload
            char *stateName = (char *)payload + 3; // Skip the "SM-" prefix

            // Call the setState method of the StateManager with the new state name
            _stateManager->setState(stateName);
            break;
          } else {
            Serial.println("Invalid state change message.");
          }


          if (_stateManager) {
            // Convert payload to char array
            char message[length];
            strncpy(message, (char *)payload, length - 1);

            // Call the handleWebSocketEvent method of the current state
            _stateManager->handleWebSocketEvent(message);
          } else {
            Serial.println("StateManager is not registered.");
          }
    
          // send message to server
          // webSocket.sendTXT("message here");
          break;
        case WStype_BIN:
          // send data to server
          // webSocket.sendBIN(payload, length);
          break;
        case WStype_ERROR:
        case WStype_FRAGMENT_TEXT_START:
        case WStype_FRAGMENT_BIN_START:
        case WStype_FRAGMENT:
        case WStype_PING:
        case WStype_PONG:
        case WStype_FRAGMENT_FIN:
          break;
      }
}

void websocket::webSocketWIFI()
{
// check for the WiFi module:
if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }

  String fv = WiFi.firmwareVersion();
  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
    Serial.println("Please upgrade the firmware");
  }

  // attempt to connect to WiFi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(SSID);
    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(SSID, PASS);

    // wait 10 seconds for connection:
    delay(10000);
  }

  Serial.println("Connected to WiFi");

  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);
}

void websocket::webSocketConnect(char ipaddress[], int port) {
    // server address, port and URL
  webSocket.begin(ipaddress, port);

  // event handler
  webSocket.onEvent(webSocketEvent);

  // try ever 5000 again if connection has failed
  webSocket.setReconnectInterval(5000);
}

void websocket::webSocketDisconnect() {
    webSocket.disconnect();
}


ServerInfo *websocket::getServers() {

  // Maximum number of servers we'll track
  const int MAX_SERVERS = 10;
  // Create a list to store the server information with proper initialization
  ServerInfo *servers[MAX_SERVERS];
  for (int i = 0; i < MAX_SERVERS; i++) {
    servers[i] = nullptr;
  }



  IPAddress localAddress = WiFi.localIP();
  int serverCount = 0;
  const int CONNECTION_TIMEOUT = 100; // milliseconds
  
  // Only scan a reasonable subset of the subnet to avoid long delays
  for (int i = 1; i < 255 && serverCount < MAX_SERVERS; i++) {
    if (i == localAddress[3]) {
      continue; // Skip the current device's IP address
    }

    // Create the IP address to scan
    char ipaddress[16];
    snprintf(ipaddress, sizeof(ipaddress), "%d.%d.%d.%d", localAddress[0], localAddress[1], localAddress[2], i);

    if(WiFi.ping(ipaddress, 5) == -1) {
      continue; // Skip if the IP address is unreachable
    }
    
    Serial.print("Scanning IP: ");
    Serial.println(ipaddress);
    
    // Try to establish a connection
    if (client.connect(ipaddress, 80)) {
      // Send HTTP request
      client.println("GET /guitargame HTTP/1.1");
      client.print("Host: ");
      client.println(ipaddress);
      client.println("Connection: close");
      client.println(); // Important: end HTTP headers with blank line
      
      // Set timeout for reading the response
      unsigned long startTime = millis();
      bool serverFound = false;
      
      // Wait for a response with timeout
      while (client.connected() && millis() - startTime < CONNECTION_TIMEOUT) {
        if (client.available()) {
          String line = client.readStringUntil('\n');
          if (line.startsWith("HTTP/1.1 200 OK")) {
            // Server found - store info
            servers[serverCount] = new ServerInfo(ipaddress, 80, "HostName", "GameName");
            serverCount++;
            serverFound = true;
            break;
          }
        }
        yield(); // Give other processes a chance to run
      }
      
      // Close the connection whether we found a server or not
      client.stop();
      
      if (serverFound) {
        Serial.print("Found server at: ");
        Serial.println(ipaddress);
      }
    } else {
      // Connection failed, clean up
      client.stop();
    }
    
    // Brief delay between connection attempts to avoid overwhelming the network
    delay(20);
  }
  
  // Create the result array with the correct size
  ServerInfo *result = nullptr;
  if (serverCount > 0) {
    result = new ServerInfo[serverCount];
    // Copy found servers to the result array
    for (int i = 0; i < serverCount; i++) {
      if (servers[i] != nullptr) {
        result[i] = *servers[i];
        delete servers[i]; // Clean up the individual ServerInfo objects
      }
    }
  } else {
    // Return an empty array if no servers found
    result = new ServerInfo[0];
  }
  
  Serial.print("Found ");
  Serial.print(serverCount);
  Serial.println(" servers");
  
  return result;
}

void websocket::webSocketLoop()
{
    webSocket.loop();
}

void websocket::registerStateManager(StateManager *stateManager) {
    _stateManager = stateManager;
}