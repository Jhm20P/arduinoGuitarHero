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

    Serial.print("Setting state to: ");
    Serial.println(stateName);

    Serial.println("State = " + String(strcmp(stateName, "MenuState")));

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
    Serial.println("Setting new state...");    // Clean up the previous state if necessary
    if (currentState) {
        Serial.println("Deleting current state...");
        State* oldState = currentState;
        currentState->destroy();  // Call destroy to clean up resources
        currentState = nullptr;  // Clear pointer before deleting
        delete oldState;
        Serial.println("Old state deleted");
    }

    // Set the new state
    Serial.println("Assigning new state...");
    if (state == nullptr) {
        Serial.println("Error: Attempted to set nullptr state");
        return;
    }
    currentState = state;
    Serial.println("New state set.");

    // Make sure we have a valid state before initializing
    if (currentState != nullptr) {
        Serial.println("Initializing new state...");
        // Add small delay to ensure hardware is ready
        delay(10);
        currentState->initDisplay();
        Serial.println("State initialization complete");
    } else {
        Serial.println("Error: Attempted to set nullptr state");
    }
}

void StateManager::loop() {
    if (!currentState) {
        Serial.println("Error: No current state set. Loop cannot proceed.");
        return;
    }

    currentState->update();

}

void StateManager::handleWebSocketEvent(char message[]) {
    // Handle the WebSocket event in the current state
    if (currentState) {
        currentState->handleWebSocketEvent(message);
    }
}