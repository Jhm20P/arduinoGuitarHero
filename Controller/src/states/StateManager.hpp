#ifndef SRC_STATES_STATEMANAGER
#define SRC_STATES_STATEMANAGER

#include "state.hpp"


class StateManager {
private:
    MKRIoTCarrier *carrier;

    // Current state
    State *currentState;
public:
    StateManager(MKRIoTCarrier *c);


    void setState(char *stateName);
    void setState(State *state);

    // State loop method
    void loop();

    virtual void handleWebSocketEvent(char message[]);
};










#endif   //SRC_STATES_STATEMANAGER
