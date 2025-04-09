#ifndef SRC_STATES_MENUSTATE
#define SRC_STATES_MENUSTATE


#include "state.hpp"

class MenuState : public State
{
public:
    MenuState(MKRIoTCarrier *c);

    void initDisplay() override;
    void update() override;
    void handleWebSocketEvent(char message[]) override;
};








#endif   //SRC_STATES_MENUSTATE
