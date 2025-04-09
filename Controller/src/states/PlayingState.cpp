#include "PlayingState.hpp"

PlayingState::PlayingState(MKRIoTCarrier *c) : State(c)
{
    // Constructor implementation
}

void PlayingState::initDisplay()
{
    // Initialize the display for the playing state
    carrier->display.setTextSize(2);
    carrier->display.setCursor(0, 0);
    carrier->display.print("Playing State");
}

void PlayingState::update()
{
    // Update the display or handle any other logic for the playing state
    carrier->display.setCursor(0, 20);
    carrier->display.print("Playing...");
}

void PlayingState::handleWebSocketEvent(char message[])
{
    // Handle the WebSocket event in the playing state
    carrier->display.setCursor(0, 40);
    carrier->display.print("WebSocket Message: ");
    carrier->display.print(message);
}