import asyncio
import socket
import queue
from models.player import Player


class GameServer:
    GameName = "Guitar Hero Game"
    HostName = socket.gethostname()
    HostIP = socket.gethostbyname(HostName)
    Port = 8765
    ConnectedClients = set()

    def __init__(self, gameName=str):
        self.GameName = gameName
        self.HostName = socket.gethostname()
        self.HostIP = socket.gethostbyname(self.HostName)
        self.Port = 8765
        self.outgoing_message_queue = queue.Queue()
        
    def add_client(self, websocket):
        """Add a new client to the connected clients set"""
        player = Player(websocket)
        self.ConnectedClients.add(player)
        print(f"New client connected: {player.player_name}")
        return player
    
    def get_client(self, websocket):
        """Get a client from the connected clients set"""
        for player in self.ConnectedClients:
            if player.websocket == websocket:
                return player
        return None
    
    def update_client(self, websocket, player):
        """Update a client's information in the connected clients set"""
        for idx, existing_player in enumerate(self.ConnectedClients):
            if existing_player.websocket == websocket:
                self.ConnectedClients[idx] = player
                print(f"Client updated: {player.player_name}")
                break

    def remove_client(self, websocket):
        """Remove a client from the connected clients set"""
        for player in self.ConnectedClients:
            if player.websocket == websocket:
                self.ConnectedClients.remove(player)
                print(f"Client disconnected: {player.player_name}")
                break    
    def send_message(self, message, websocket):
        """Queue a message to be sent to a specific client"""
        # Add a tuple (message, recipient) to the queue
        self.outgoing_message_queue.put(("direct", message, websocket))
        print(f"Message queued for sending to a specific client: {message}")

    def broadcast_message(self, message):
        """Queue a message to be sent to all connected clients"""
        # Add a tuple (message, None) to the queue to indicate broadcast
        self.outgoing_message_queue.put(("broadcast", message, None))
        print(f"Broadcast message queued for sending: {message}")
    def get_queued_messages(self):
        """Get any queued messages to be sent to clients"""
        messages = []
        # Get all available messages from the queue
        while not self.outgoing_message_queue.empty():
            messages.append(self.outgoing_message_queue.get())
        return messages

    def to_dict(self):
        return {
            "game_name": self.GameName,
            "hostname": self.HostName,
            "ip": self.HostIP,
            "port": self.Port
        }