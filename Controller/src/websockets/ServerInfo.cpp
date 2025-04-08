#include "ServerInfo.hpp"

ServerInfo::ServerInfo(char *ipaddress, int port, char *HostName, char *GameName) {
    this->ipaddress = ipaddress;
    this->port = port;
    this->HostName = HostName;
    this->GameName = GameName;
}

ServerInfo::ServerInfo() {
}