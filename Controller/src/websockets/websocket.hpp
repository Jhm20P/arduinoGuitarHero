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
        static ServerInfo* servers[10];
        static int serverCount;
        static int currentScanIndex;
        static unsigned long lastScanTime;
    public:
        static void initServerScan();
        static void updateServerScan();
        static ServerInfo** getScannedServers();
        static void webSocketSend(char message[]);
        static void webSocketEvent(WStype_t type, uint8_t *payload, size_t length);
        static void webSocketConnect(char ipaddress[], int port);
        static void webSocketDisconnect();
        static void webSocketWIFI();
        static void webSocketLoop();
        static int getServerPort(char ipaddress[]);
        static void registerStateManager(StateManager *stateManager);
};


#endif