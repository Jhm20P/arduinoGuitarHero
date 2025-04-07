"""
Network Manager for Guitar Hero Game
Coordinates HTTP and WebSocket servers
"""
import time
import queue
from networking.http_server import GameDiscoveryServer
from networking.websocket_server import GameWebSocketServer

class NetworkManager:
    """
    Manages all networking services for the Guitar Hero Game
    """
    def __init__(self):
        self.http_server = None
        self.websocket_server = None
        self.game_server = None
        self.message_queue = queue.Queue()
        self.http_port = 80
        self.is_running = False
    
    def start_services(self, game_server):
        """Start all network services with the provided game server"""
        if self.is_running:
            self.stop_services()
            # Allow time for ports to be released
            time.sleep(1)
        
        self.game_server = game_server
        self.is_running = True
        
        # Start HTTP discovery service
        self.http_server = GameDiscoveryServer(game_server, port=self.http_port)
        self.http_server.start()
        
        # Start WebSocket server for controller communication
        self.websocket_server = GameWebSocketServer(game_server, self.message_queue)
        self.websocket_server.start()
        
        return True
    
    def stop_services(self):
        """Stop all network services"""
        if not self.is_running:
            return
            
        # Stop WebSocket server
        if self.websocket_server:
            self.websocket_server.stop()
            self.websocket_server = None
        
        # Stop HTTP server
        if self.http_server:
            self.http_server.stop()
            self.http_server = None
        
        # Clear message queue
        while not self.message_queue.empty():
            self.message_queue.get()
        
        self.is_running = False
        self.game_server = None
    
    def process_messages(self):
        """Process all messages in the queue"""
        messages = []
        
        # Get all messages from the queue without blocking
        while not self.message_queue.empty():
            try:
                message = self.message_queue.get_nowait()
                messages.append(message)
            except queue.Empty:
                break
                
        return messages