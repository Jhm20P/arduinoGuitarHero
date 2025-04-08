#include "MenuState.hpp"
#include "websockets/websocket.hpp"

MenuState::MenuState(MKRIoTCarrier *c) : State(c)
{
    // Constructor implementation
}

void MenuState::initDisplay()
{
    // Initialize the display for the menu state
    
    carrier->display.setTextSize(2);
    carrier->display.setCursor(0, 0);
    carrier->display.print("Menu State");
}


