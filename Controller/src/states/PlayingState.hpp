#ifndef SRC_STATES_PLAYINGSTATE
#define SRC_STATES_PLAYINGSTATE

#include "state.hpp"
#include "Arduino.h"
#include <vector>

// Define a simple struct for tracking notes
struct Note {
    int track;          // Track number (0-3)
    long timeMs;        // Time in ms when the note should be hit
    bool hit;           // Whether the note has been hit
};

class PlayingState : public State
{
private:
    /* data */
    String playerName;
    int score = 0;
    long gamestarttime = 0;
    
    // Note tracking
    std::vector<Note> upcomingNotes;      // Store upcoming notes
    const int HIT_WINDOW_MS = 200;        // Time window to hit a note (±100ms)
    const int PERFECT_HIT_POINTS = 100;   // Points for perfect hit
    const int GOOD_HIT_POINTS = 50;       // Points for good hit
    
    // Track button states to detect changes
    bool prevButtonStates[5] = {false, false, false, false, false};
    
    // Helper functions
    void processNoteHit(int trackNum);
    void flashLED(int ledNum);
    void parseNoteMessage(const char* message);

public:
    PlayingState(MKRIoTCarrier *c);

    void initDisplay() override;
    void update() override;
    void handleWebSocketEvent(char message[]) override;
    void destroy() override;

    void disconnect();
};

#endif   //SRC_STATES_PLAYINGSTATE
