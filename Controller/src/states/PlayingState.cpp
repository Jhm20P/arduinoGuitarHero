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