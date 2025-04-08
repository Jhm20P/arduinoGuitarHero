#ifndef WEBSOCKETS_HPP
#define WEBSOCKETS_HPP
#include <BetterWiFiNINA.h>
#include <WebSocketsClient.h>
#include <states/StateManager.hpp>

class ServerInfo;

class websocket {
    private:
        static StateManager *_stateManager;
        static WiFiClient client;
        static WebSocketsClient webSocket;
    public:
        static void webSocketSend(char message[]);
        static void webSocketEvent(WStype_t type, uint8_t *payload, size_t length);
        static void webSocketConnect(char ipaddress[], int port);
        static void webSocketDisconnect();
        static ServerInfo *getServers();
        static void webSocketWIFI();
        static void webSocketLoop();

        static void registerStateManager(StateManager *stateManager);
};


#endif