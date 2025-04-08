#ifndef WEBSOCKETS_HPP
#define WEBSOCKETS_HPP
#include <BetterWiFiNINA.h>
#include <WebSocketsClient.h>
class websocket {
    public:
        static void webSocketEvent(WStype_t type, uint8_t *payload, size_t length);
        static void webSocketWIFI();
        static void webSocketLoop();
};


#endif