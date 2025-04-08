#ifndef SRC_STATES_MENUSTATE
#define SRC_STATES_MENUSTATE


#include "state.hpp"

class MenuState : public State
{
private:
    MKRIoTCarrier *carrier;
public:
    MenuState(MKRIoTCarrier *c);

    void initDisplay() override;
};








#endif   //SRC_STATES_MENUSTATE
