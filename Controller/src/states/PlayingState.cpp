#include "PlayingState.hpp"
#include "websockets/websocket.hpp"
#include <algorithm>  // For std::sort

PlayingState::PlayingState(MKRIoTCarrier *c) : State(c)
{
    // Constructor implementation
}

void PlayingState::initDisplay()
{
    // Initialize the display for the playing state
    carrier->display.fillScreen(ST7735_BLACK);
    carrier->display.setTextSize(1);
    carrier->display.setTextColor(ST7735_WHITE);

    // Colour order Red Green Yellow Blue

    uint32_t red = carrier->leds.Color(255, 0, 0);
    uint32_t green = carrier->leds.Color(0, 255, 0);
    uint32_t white = carrier->leds.Color(255, 255, 255);
    uint32_t yellow = carrier->leds.Color(255, 255, 0);
    uint32_t blue = carrier->leds.Color(0, 0, 255);

    carrier->leds.fill(red, 0, 1);
    carrier->leds.fill(green, 1, 1);
    carrier->leds.fill(white, 2, 1);
    carrier->leds.fill(yellow, 3, 1);
    carrier->leds.fill(blue, 4, 1);
    carrier->leds.setBrightness(30);
    carrier->leds.show(); // Update the LED strip
}

void PlayingState::update()
{
    // Update the display or handle any other logic for the playing state
    carrier->display.fillRect(0, 0, 160, 128, ST7735_BLACK); // Clear the display
    carrier->display.setCursor(20, 60);
    carrier->display.print("Player name: ");
    carrier->display.print(playerName);
    carrier->display.setCursor(20, 80);
    carrier->display.print("Score: ");
    carrier->display.print(score);

    // Get current button states
    bool buttonStates[4];
    buttonStates[0] = carrier->Button0.getTouch();
    buttonStates[1] = carrier->Button1.getTouch();
    buttonStates[2] = carrier->Button2.getTouch();
    buttonStates[3] = carrier->Button3.getTouch();
    bool disconnectButton = carrier->Button4.getTouch();
    
    // Check for disconnect button press
    if (disconnectButton && !prevButtonStates[4]) {
        disconnect();
    }
    prevButtonStates[4] = disconnectButton;
    
    // Check if any button was just pressed (transition from not pressed to pressed)
    for (int i = 0; i < 4; i++) {
        if (buttonStates[i] && !prevButtonStates[i]) {
            // Button was just pressed, check for note hit
            processNoteHit(i);
        }
        prevButtonStates[i] = buttonStates[i];
    }
    
    // Clean up expired notes (notes that are too old to hit)
    if (gamestarttime > 0 && !upcomingNotes.empty()) {
        long currentGameTime = millis() - gamestarttime;
        
        // Remove notes that are too old to hit
        while (!upcomingNotes.empty() && 
               (upcomingNotes[0].hit || currentGameTime > upcomingNotes[0].timeMs + (HIT_WINDOW_MS/2))) {
            upcomingNotes.erase(upcomingNotes.begin());
        }
    }
}

void PlayingState::processNoteHit(int trackNum)
{
    if (gamestarttime == 0) return; // Game hasn't started yet
    
    long currentGameTime = millis() - gamestarttime;
    int pointsAwarded = 0;
    
    // Flash the corresponding LED to give feedback
    //flashLED(trackNum);
    
    // Check if there's a note to hit on this track
    for (size_t i = 0; i < upcomingNotes.size(); i++) {
        Note& note = upcomingNotes[i];
        
        // Only process notes for the correct track that haven't been hit yet
        if (note.track == trackNum && !note.hit) {
            // Calculate timing accuracy
            long timeDiff = abs(currentGameTime - note.timeMs);
            
            // Check if the note is within the hit window
            if (timeDiff <= HIT_WINDOW_MS/2) {
                note.hit = true;
                
                // Award points based on timing accuracy
                if (timeDiff <= HIT_WINDOW_MS/4) {
                    // Perfect hit (within 50ms)
                    pointsAwarded = PERFECT_HIT_POINTS;
                    Serial.println("Perfect hit!");
                } else {
                    // Good hit (within 100ms)
                    pointsAwarded = GOOD_HIT_POINTS;
                    Serial.println("Good hit!");
                }
                
                // Update score
                score += pointsAwarded;
                Serial.print("Score: ");
                Serial.println(score);
                
                break; // Only hit one note per button press
            }
        }
    }
}

void PlayingState::flashLED(int ledNum)
{
    // Get the current color of the LED
    uint32_t currentColor;
    switch(ledNum) {
        case 0: currentColor = carrier->leds.Color(255, 0, 0); break;    // Red
        case 1: currentColor = carrier->leds.Color(0, 255, 0); break;    // Green
        case 2: currentColor = carrier->leds.Color(255, 255, 0); break;  // Yellow
        case 3: currentColor = carrier->leds.Color(0, 0, 255); break;    // Blue
        default: currentColor = carrier->leds.Color(255, 255, 255); break; // White
    }
    
    // Flash white then return to original color
    carrier->leds.setPixelColor(ledNum, carrier->leds.Color(255, 255, 255));
    carrier->leds.show();
    
    // Original color will be restored on next frame
    // No delay needed as the update function will be called frequently
}

void PlayingState::parseNoteMessage(const char* message)
{
    // Format: "NOTE-<track-number>-<time-in-ms-since-start>"
    // Extract track number
    char* trackStart = strstr(message, "NOTE-");
    if (!trackStart) return;
    
    trackStart += 5; // Skip "NOTE-"
    int track = atoi(trackStart);
    
    // Extract time
    char* timeStart = strchr(trackStart, '-');
    if (!timeStart) return;
    
    timeStart++; // Skip '-'
    long timeMs = atol(timeStart);
    
    // Add to upcoming notes
    Note newNote = {track, timeMs, false};
    upcomingNotes.push_back(newNote);
    
    // Sort notes by time (keep them in chronological order)
    std::sort(upcomingNotes.begin(), upcomingNotes.end(), 
        [](const Note& a, const Note& b) {
            return a.timeMs < b.timeMs;
        });
    
    Serial.print("Added note - Track: ");
    Serial.print(track);
    Serial.print(", Time: ");
    Serial.println(timeMs);
}

void PlayingState::disconnect()
{
    websocket::_stateManager->setState("MenuState"); // Change the state to MenuState
}

void PlayingState::destroy()
{
    // Clean up resources or reset the display for the playing state
    websocket::webSocketDisconnect(); // Disconnect the WebSocket
    carrier->display.fillScreen(ST7735_BLACK);
    carrier->leds.fill(0, 0, 5); // Turn off all LEDs
    carrier->leds.show(); // Update the LED strip
}

void PlayingState::handleWebSocketEvent(char message[])
{
    Serial.println(message); // Print the received message for debugging

    // If the message starts with "PlayerObject", extract the player name from the line that starts with "Player="
    if (strncmp(message, "PlayerObject", 12) == 0) {
        char *playerNameStart = strstr(message, "Player=");
        if (playerNameStart != nullptr) {
            playerNameStart += strlen("Player=");
            char *playerNameEnd = strstr(playerNameStart, "\n");
            if (playerNameEnd != nullptr) {
                *playerNameEnd = '\0'; // Null-terminate the string
                playerName = String(playerNameStart); // Convert to String
            }
        }
    }
    // If the message starts with "Game-" then handle the game events
    else if (strncmp(message, "Game-", 5) == 0) {
        // Extract the game event from the message
        char *event = message + 5; // Skip the "Game-" prefix
        
        // If event is "Start", set the game start time
        if (strncmp(event, "Start", 5) == 0) {
            gamestarttime = millis(); // Set the game start time
            // Clear any existing notes when game starts
            upcomingNotes.clear();
            score = 0;
        } else if (strncmp(event, "End", 3) == 0) {
            // Handle game end event
            long gameEndTime = millis(); // Get the current time
            long gameDuration = gameEndTime - gamestarttime; // Calculate the game duration
            Serial.print("Game duration: ");
            Serial.println(gameDuration); // Print the game duration for debugging
            
            // Display final score
            carrier->display.fillScreen(ST7735_BLACK);
            carrier->display.setCursor(20, 50);
            carrier->display.setTextSize(2);
            carrier->display.println("Game Over!");
            carrier->display.setCursor(20, 80);
            carrier->display.print("Final Score: ");
            carrier->display.println(score);
            carrier->display.setTextSize(1);
        }
    }
    // If the message starts with "NOTE-" then process the note
    else if (strncmp(message, "NOTE-", 5) == 0) {
        parseNoteMessage(message);
    }
}