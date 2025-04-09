#ifndef SRC_STATES_PLAYINGSTATE
#define SRC_STATES_PLAYINGSTATE

#include "state.hpp"

class PlayingState : public State
{
private:
    /* data */
    MKRIoTCarrier *carrier;
public:
    PlayingState(MKRIoTCarrier *c);

    void initDisplay() override;
    void update() override;
    void handleWebSocketEvent(char message[]) override;

};









#endif   //SRC_STATES_PLAYINGSTATE
