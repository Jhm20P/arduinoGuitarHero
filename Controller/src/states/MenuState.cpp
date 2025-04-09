#include "MenuState.hpp"
#include "websockets/websocket.hpp"
#include "websockets/ServerInfo.hpp"

MenuState::MenuState(MKRIoTCarrier *c) : State(c)
{
    // Constructor implementation
}

void MenuState::initDisplay()
{
    // Initialize the display for the menu state
    Serial.println("Initializing MenuState display...");
    websocket::initServerScan();
    Serial.println("Server scan initialized.");

    // Debug info to check carrier validity
    if (carrier == nullptr) {
        Serial.println("ERROR: carrier is null!");
        return;
    }
    Serial.println("Carrier pointer is valid.");
    

        carrier->display.fillScreen(ST7735_BLACK);
        Serial.println("fillScreen completed");
        
        carrier->display.setTextColor(ST7735_WHITE);
        Serial.println("setTextColor completed");
        
        carrier->display.setTextSize(2);
        Serial.println("setTextSize completed");
        
        carrier->display.setCursor(0, 0);
        Serial.println("setCursor completed");
        
        carrier->display.print("Menu State");
        Serial.println("print completed");
        
        Serial.println("MenuState display initialized.");
        carrier->display.setTextSize(1);
    
}

void MenuState::update()
{
    // Update the display or handle any other logic for the menu state
    carrier->display.setCursor(5, 20);
    carrier->display.print("Scanning for servers...");
    
    // websocket::updateServerScan();

    auto buttonUp = carrier->Button1.getTouch();
    carrier->Buttons.update(); // Update the touch buttons state
    auto buttonDown = carrier->Button0.getTouch();
    carrier->Buttons.update(); // Update the touch buttons state
    auto buttonSelect = carrier->Buttons.onTouchDown(TOUCH2);
    carrier->Buttons.update(); // Update the touch buttons state



    // check if any button is pressed, and change the text color of the currently sellected server 
    // to red, and the others to white

    static int selectedServerIndex = 0; // Track the currently selected server index
    ServerInfo** servers = websocket::getScannedServers();
    if (servers != nullptr) {
        int serverCount = 0;
        while (servers[serverCount] != nullptr) {
            serverCount++;
        }


        if (buttonUp) {
            selectedServerIndex = (selectedServerIndex - 1 + serverCount) % serverCount;
        } else if (buttonDown) {
            selectedServerIndex = (selectedServerIndex + 1) % serverCount;
        } else if (buttonSelect && !isConnected) {
            // Send connection request to the selected server
            sendConnectionRequest(servers[selectedServerIndex]->ipaddress, servers[selectedServerIndex]->port);
            Serial.print("MenuState: Sending connection request to server at ");
            Serial.print(servers[selectedServerIndex]->ipaddress);
            Serial.print(":");
            Serial.println(servers[selectedServerIndex]->port);
        }
        for (int i = 0; i < serverCount; i++) {
            carrier->display.setCursor(5, 80 + (i * 10));
            if (i == selectedServerIndex) {
                carrier->display.setTextColor(ST7735_RED);
            } else {
                carrier->display.setTextColor(ST7735_WHITE);
            }
            carrier->display.print(servers[i]->HostName);
            carrier->display.print(", ");
            carrier->display.setCursor(120, 80 + (i * 10));
            carrier->display.print("IP: ");
            carrier->display.print(servers[i]->ipaddress);
        }
    } else {
        carrier->display.setCursor(5, 80);
        carrier->display.print("No servers found.");
    }

}

void MenuState::sendConnectionRequest(char ipaddress[], int port)
{
    // Send a connection request to the specified IP address and port
    isConnected = true;
    Serial.print("Connecting to server at ");
    Serial.print(ipaddress);
    Serial.print(":");
    Serial.println(port);
    auto portNumber = websocket::getServerPort(ipaddress);
    Serial.print("Port number: ");
    Serial.println(portNumber);
    websocket::webSocketConnect(ipaddress, portNumber);
    
}

void MenuState::handleWebSocketEvent(char message[])
{
    // Handle the WebSocket event in the menu state
    // Should not be called in this state
}