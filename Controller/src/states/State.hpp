#ifndef SRC_STATES_STATE
#define SRC_STATES_STATE

#include <WebSockets.h>
#include <Arduino_MKRIoTCarrier.h>

class State {
    protected:
        MKRIoTCarrier *carrier;
    private:
    public:
        State(MKRIoTCarrier *c);

        
        virtual void initDisplay();
        virtual void handleWebSocketEvent(char message[]);

        virtual void update();
};











#endif   //SRC_STATES_STATE
