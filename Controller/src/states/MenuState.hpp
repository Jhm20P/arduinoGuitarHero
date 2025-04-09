#ifndef SRC_STATES_MENUSTATE
#define SRC_STATES_MENUSTATE


#include "state.hpp"

class MenuState : public State
{
private:
    bool isConnected = false;
public:
    MenuState(MKRIoTCarrier *c);

    void initDisplay() override;
    void update() override;
    void handleWebSocketEvent(char message[]) override;
    void destroy() override;
    
    void sendConnectionRequest(char ipaddress[], int port);
};








#endif   //SRC_STATES_MENUSTATE
