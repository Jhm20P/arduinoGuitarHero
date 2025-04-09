#include "State.hpp"

State::State(MKRIoTCarrier *c)
{
    carrier = c;
}

void State::initDisplay() {
    // Default empty implementation
}

void State::handleWebSocketEvent(char message[]) {
    // Default empty implementation
}

void State::update() {
    // Default empty implementation
}