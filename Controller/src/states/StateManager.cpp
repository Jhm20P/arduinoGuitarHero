#include "StateManager.hpp"
#include "MenuState.hpp"
#include "PlayingState.hpp"

StateManager::StateManager(MKRIoTCarrier *c) {
    carrier = c;
    currentState = nullptr; // Initialize currentState to nullptr
}

void StateManager::setState(char *stateName) {
    // Here you would typically have a mapping of state names to state instances
    // For simplicity, let's assume we have a function that creates the state based on the name
    State *newState = nullptr;

    if (strcmp(stateName, "MenuState") == 0) {
        newState = new MenuState(carrier);
    } else if (strcmp(stateName, "PlayingState") == 0) {
        newState = new PlayingState(carrier);
    } else {
        Serial.println("Unknown state name.");
        return;
    }

    setState(newState);
}

void StateManager::setState(State *state) {
    // Clean up the previous state if necessary
    if (currentState) {
        delete currentState;
    }

    // Set the new state
    currentState = state;

    // Initialize the new state
    if (currentState) {
        currentState->initDisplay();
    }
}

void StateManager::loop() {
    // Call the loop method of the current state
    if (currentState) {
        currentState->update();
    }
}

void StateManager::handleWebSocketEvent(char message[]) {
    // Handle the WebSocket event in the current state
    if (currentState) {
        currentState->handleWebSocketEvent(message);
    }
}