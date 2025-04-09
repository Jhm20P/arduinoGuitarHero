#include "MenuState.hpp"
#include "websockets/websocket.hpp"

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


    carrier->display.fillScreen(ST7735_BLACK);
    carrier->display.setTextColor(ST7735_WHITE);
    carrier->display.setTextSize(2);
    carrier->display.setCursor(0, 0);
    carrier->display.print("Menu State");
    Serial.println("MenuState display initialized.");
}

void MenuState::update()
{
    // Update the display or handle any other logic for the menu state
    carrier->display.setCursor(0, 20);
    carrier->display.print("Scanning for servers...");
    
    websocket::updateServerScan();
    
    ServerInfo* server = websocket::getScannedServers();
    if (server != nullptr) {
        carrier->display.setCursor(0, 40);
        carrier->display.print("Found server: ");
        carrier->display.print("");
    } else {
        carrier->display.setCursor(0, 40);
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