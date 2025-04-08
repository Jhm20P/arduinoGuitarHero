#ifndef SERVERINFO
#define SERVERINFO


class ServerInfo
{
    private:
        /* data */
    public:
        char *ipaddress;
        int port;
        char *HostName;
        char *GameName;
        ServerInfo(char *ipaddress, int port, char *HostName, char *GameName);
        ServerInfo();
};

#endif   //SRC_WEBSOCKETS_SERVERINFO
