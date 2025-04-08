#ifndef SRC_STATES_STATE
#define SRC_STATES_STATE

#include <WebSockets.h>
#include <Arduino_MKRIoTCarrier.h>

class State {
private:
    MKRIoTCarrier *carrier;
public:
    State(MKRIoTCarrier *c);

    
    virtual void initDisplay();
    virtual void handleWebSocketEvent(char message[]);

    void update();
};











#endif   //SRC_STATES_STATE
