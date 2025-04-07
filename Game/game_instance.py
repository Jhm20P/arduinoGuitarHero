import asyncio
import pygame
import websockets
import json
import socket
import threading
import queue
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from guitarherogame import GameServer

class GameInstance:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Guitar Hero Game")
        
        # Screen dimensions
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Game state
        self.running = True
        self.current_screen = None
        
        # Server settings
        self.game_server = None
        self.http_thread = None
        self.websocket_thread = None
        self.websocket_loop = None
        self.message_queue = queue.Queue()  # Queue to handle incoming messages
        
        # HTTP server port (use a non-privileged port)
        self.http_port = 80
        
    def start(self):
        """Start the game loop"""
        # Import here to avoid circular imports
        from screens.main_menu import MainMenuScreen
        
        # Set initial screen
        self.current_screen = MainMenuScreen(self)
        
        # Main game loop
        while self.running:
            # Process events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    
            # Handle events for current screen
            self.current_screen.handle_events(events)
            
            # Update screen logic
            self.current_screen.update()
            
            # Check for screen transition
            next_screen = self.current_screen.get_next_screen()
            if next_screen:
                self.current_screen = next_screen
            
            # Draw current screen
            self.current_screen.draw(self.screen)
            
            # Update display
            pygame.display.flip()
            self.clock.tick(self.fps)
        
        # Clean up
        self.stop_server()
        pygame.quit()
    
    def create_game_server(self, game_name):
        """Create and start the game server with the specified name"""
        try:
            self.game_server = GameServer(game_name)
            
            # Start HTTP server for discovery
            self.http_thread = threading.Thread(target=self.start_http_server, daemon=True)
            self.http_thread.start()
            
            # Start WebSocket server in a way that properly handles the event loop
            self.websocket_thread = threading.Thread(target=self.start_websocket_server, daemon=True)
            self.websocket_thread.start()
            
            print(f"Game server created: {game_name}")
            print(f"Server running at: {self.game_server.HostIP}:{self.game_server.Port}")
            print(f"HTTP discovery service running at: http://{self.game_server.HostIP}:{self.http_port}/guitargame")
        except Exception as e:
            print(f"Error creating game server: {e}")
            import traceback
            traceback.print_exc()
    
    def start_websocket_server(self):
        """Start the WebSocket server using asyncio.run() which properly manages the event loop"""
        try:
            # This is the key change - using asyncio.run() which properly manages the event loop
            asyncio.run(self.run_websocket_server())
        except Exception as e:
            print(f"Error in WebSocket server thread: {e}")
            import traceback
            traceback.print_exc()
    
    async def run_websocket_server(self):
        """The async function that runs the WebSocket server"""
        try:
            # Start WebSocket server
            server = await websockets.serve(self.handle_client, "0.0.0.0", self.game_server.Port)
            print(f"WebSocket server started successfully on port {self.game_server.Port}")
            
            # Keep the server running until the program ends
            await server.wait_closed()
        except Exception as e:
            print(f"Error running WebSocket server: {e}")
            import traceback
            traceback.print_exc()
            
    def start_http_server(self):
        """Start HTTP server for game discovery"""
        try:
            class CustomHandler(BaseHTTPRequestHandler):
                def do_GET(self_handler):
                    try:
                        if self_handler.path == "/guitargame":
                            if self.game_server:
                                response = json.dumps(self.game_server.to_dict())
                                self_handler.send_response(200)
                                self_handler.send_header("Content-Type", "application/json")
                                self_handler.end_headers()
                                self_handler.wfile.write(response.encode())
                                print(f"Responded to HTTP service discovery with: {response}")
                            else:
                                self_handler.send_response(503)  # Service Unavailable
                                self_handler.end_headers()
                        else:
                            self_handler.send_response(404)
                            self_handler.end_headers()
                    except Exception as e:
                        print(f"Error in HTTP handler: {e}")
                
                def log_message(self, format, *args):
                    # Suppress noisy HTTP server logs
                    pass
            
            # Use a non-privileged port that doesn't require admin rights
            server_address = ("0.0.0.0", self.http_port)
            http_server = HTTPServer(server_address, CustomHandler)
            print(f"HTTP server for service discovery started on http://0.0.0.0:{self.http_port}")
            http_server.serve_forever()
        except Exception as e:
            print(f"Error starting HTTP server: {e}")
            import traceback
            traceback.print_exc()
    
    async def handle_client(self, websocket):
        """Handle client websocket connections"""
        try:
            # Register client
            print(f"Client connected: {websocket.remote_address}")
            if self.game_server:
                self.game_server.ConnectedClients.add(websocket)
            
            try:
                # Keep connection open and handle messages
                async for message in websocket:
                    try:
                        # Process incoming message
                        print(f"Received message: {message}")
                        
                        # Put message in queue for game processing
                        self.message_queue.put(message)
                        
                        # Echo the message back
                        await websocket.send(f"Server received: {message}")
                        
                    except Exception as e:
                        print(f"Error processing message: {e}")
            
            except websockets.exceptions.ConnectionClosed:
                print(f"Connection closed with client: {websocket.remote_address}")
            
            finally:
                # Unregister client when connection is closed
                if self.game_server and websocket in self.game_server.ConnectedClients:
                    self.game_server.ConnectedClients.remove(websocket)
        except Exception as e:
            print(f"Error in handle_client: {e}")
    
    def process_messages(self):
        """Process messages from the queue"""
        # Process all available messages
        try:
            while not self.message_queue.empty():
                message = self.message_queue.get()
                try:
                    # For example, if message contains note data:
                    # Parse message and add notes to the game
                    # This is just an example - actual implementation would depend on message format
                    
                    # Assuming messages are integers representing tracks (0-3)
                    try:
                        track = int(message)
                        if 0 <= track < 4:
                            # If we're on the playing screen, add a note
                            if hasattr(self.current_screen, 'add_note'):
                                self.current_screen.add_note(track)
                    except ValueError:
                        # Not a valid track number
                        pass
                        
                except Exception as e:
                    print(f"Error processing message from queue: {e}")
        except Exception as e:
            print(f"Error in process_messages: {e}")
    
    async def broadcast_message(self, message):
        """Send a message to all connected clients"""
        try:
            if self.game_server and self.game_server.ConnectedClients:
                await asyncio.gather(
                    *[client.send(message) for client in self.game_server.ConnectedClients]
                )
        except Exception as e:
            print(f"Error broadcasting message: {e}")
    
    def stop_server(self):
        """Stop the server if it's running"""
        # The WebSocket and HTTP servers are run in daemon threads
        # which will automatically terminate when the main program exits
        print("Server shutdown initiated")


if __name__ == "__main__":
    game = GameInstance()
    game.start()