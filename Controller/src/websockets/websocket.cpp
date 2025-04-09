#include <Arduino.h>
#include <ArduinoJson.h>
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

ServerInfo* websocket::servers[10] = { nullptr };
int websocket::serverCount = 0;
int websocket::currentScanIndex = 1;
unsigned long websocket::lastScanTime = 0;

void websocket::initServerScan() {
    serverCount = 0;
    currentScanIndex = 1;
    lastScanTime = 0;
    for (int i = 0; i < 10; i++) {
        servers[i] = nullptr;
    }
}

void websocket::updateServerScan() {
    if (millis() - lastScanTime < 10) return; // throttle scan rate
    lastScanTime = millis();

    IPAddress localIP = WiFi.localIP();

    for (int i = 0; i < 3 && currentScanIndex < 255; i++) {
        if (currentScanIndex == localIP[3]) {
            currentScanIndex++;
            continue;
        }

        char ipaddress[16];
        snprintf(ipaddress, sizeof(ipaddress), "%d.%d.%d.%d",
                localIP[0], localIP[1], localIP[2], currentScanIndex);

        Serial.print("Scanning IP: ");
        Serial.println(ipaddress);

        if (WiFi.ping(ipaddress, 5) != -1) {
            if (client.connect(ipaddress, 80)) {
                client.println("GET /guitargame HTTP/1.1");
                client.print("Host: ");
                client.println(ipaddress);
                client.println("Connection: close");
                client.println();

                unsigned long timeout = millis() + 50;
                while (millis() < timeout && client.connected()) {
                    if (client.available()) {
                        String line = client.readStringUntil('\n');
                        if (line.startsWith("HTTP/1.1 200 OK")) {
                            if (serverCount < 10) {
                                servers[serverCount++] = new ServerInfo(ipaddress, 80, "HostName", "GameName");
                                Serial.print("Found server at: ");
                                Serial.println(ipaddress);
                            }
                            break;
                        }
                    }
                    yield();
                }

                client.stop();
            }
        }

        currentScanIndex++;
    }
}

ServerInfo** websocket::getScannedServers() {
    // Check if servers are already initialized to avoid memory leaks
    static bool serversInitialized = false;
    
    if (!serversInitialized) {
        // Clean up any existing server data first
        for (int i = 0; i < 10; i++) {
            if (servers[i] != nullptr) {
                delete servers[i];
                servers[i] = nullptr;
            }
        }
        
        // Hardcoded test servers - only create once
        servers[0] = new ServerInfo("192.168.0.14", 80, "HostName", "GameName");
        servers[1] = new ServerInfo("192.168.0.15", 80, "HostName2", "GameName2");
        servers[2] = new ServerInfo("192.168.0.16", 80, "HostName3", "GameName3");
        servers[3] = new ServerInfo("192.168.0.17", 80, "HostName4", "GameName4");
        
        // Ensure null termination of the array
        for (int i = 4; i < 10; i++) {
            servers[i] = nullptr;
        }
        
        serverCount = 4;
        serversInitialized = true;
    }
    
    return servers;
}

int websocket::getServerPort(char ipaddress[]) {
    // Make HTTP GET request to target IP address at endpoint /guitargame
    char request[128];
    snprintf(request, sizeof(request), "GET /guitargame HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n", ipaddress);

    Serial.print("Connecting to server at: ");
    Serial.println(ipaddress);

    if (client.connect(ipaddress, 80)) {
        Serial.println("Connection successful.");

        Serial.println("Sending HTTP request:");
        Serial.println(request);
        client.print(request);

        unsigned long timeout = millis() + 10000; // 10-second timeout
        String fullResponse = ""; // Capture the full response

        while (millis() < timeout && client.connected()) {
            while (client.available()) {
                String line = client.readStringUntil('\n');
                Serial.print("Received line: ");
                Serial.println(line);
                fullResponse += line + "\n"; // Append to full response
            }
            yield();
        }

        Serial.println("Full Response:");
        Serial.println(fullResponse);

        // Attempt to find and parse JSON in the full response
        int jsonStart = fullResponse.indexOf("{");
        if (jsonStart != -1) {
            String jsonString = fullResponse.substring(jsonStart);
            Serial.print("Extracted JSON: ");
            Serial.println(jsonString);

            StaticJsonDocument<256> doc;
            DeserializationError error = deserializeJson(doc, jsonString);
            if (error) {
                Serial.print("Deserialization Error: ");
                Serial.println(error.c_str());
            } else {
                const char* gameName = doc["game_name"];
                const char* hostname = doc["hostname"];
                const char* ip = doc["ip"];
                int port = doc["port"];

                Serial.print("Game Name: ");
                Serial.println(gameName);
                Serial.print("Host Name: ");
                Serial.println(hostname);
                Serial.print("IP: ");
                Serial.println(ip);
                Serial.print("Port: ");
                Serial.println(port);

                return port; // Return the parsed port
            }
        } else {
            Serial.println("No JSON found in response.");
        }

        client.stop();
    } else {
        Serial.println("Connection failed.");
    }

    return -1; // Not found
}

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
            Serial.print("Invalid state change message: ");
            Serial.println((char *)payload);
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


void websocket::webSocketLoop()
{
    webSocket.loop();
}

void websocket::registerStateManager(StateManager *stateManager) {
    _stateManager = stateManager;
}