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
    
}

void MenuState::update()
{
    // Update the display or handle any other logic for the menu state
    carrier->display.setCursor(5, 20);
    carrier->display.print("Scanning for servers...");
    
    // websocket::updateServerScan();

    auto buttonUp = carrier->Buttons.onTouchDown(TOUCH1);
    auto buttonDown = carrier->Buttons.onTouchDown(TOUCH0);
    auto buttonSelect = carrier->Buttons.onTouchDown(TOUCH2);

    // check if any button is pressed, and change the text color of the currently sellected server 
    // to red, and the others to white

        // Call the server scan function and display results
       // websocket::updateServerScan();
    
    ServerInfo** servers = websocket::getScannedServers();
        if (servers != nullptr) {
            carrier->display.setTextSize(1);
            carrier->display.setCursor(5, 80);
            carrier->display.print("Found server: ");
            for(int i = 0; i < sizeof(servers); i++){
            carrier->display.setCursor(5, 80 + (i * 10));
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


void MenuState::handleWebSocketEvent(char message[])
{
    // Handle the WebSocket event in the menu state
    carrier->display.setCursor(0, 60);
    carrier->display.print("WebSocket Message: ");
    carrier->display.print(message);
}