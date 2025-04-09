"""
WebSocket Server for Guitar Hero Game
Handles real-time communication with game controllers
"""
import asyncio
import threading
import websockets
import time
from models.game_server import GameServer
from models.player import Player

class GameWebSocketServer:
    """
    WebSocket server for Guitar Hero Game
    """
    game_server: GameServer = None

    def __init__(self, game_server:GameServer, message_queue):
        self.game_server = game_server
        self.message_queue = message_queue
        self.websocket_thread = None
        self.stop_event = threading.Event()
        self.is_running = False
    
    def start(self):
        """Start the WebSocket server"""
        if self.is_running:
            print("WebSocket server already running")
            return
        
        try:
            # Reset stop event
            self.stop_event.clear()
            self.is_running = True
            
            # Start WebSocket server in a way that properly handles the event loop
            self.websocket_thread = threading.Thread(target=self._start_server_thread, daemon=True)
            self.websocket_thread.start()
            
            print(f"Starting WebSocket server on port {self.game_server.Port}...")
        except Exception as e:
            print(f"Error starting WebSocket server: {e}")
            import traceback
            traceback.print_exc()
    
    def _start_server_thread(self):
        """Start the WebSocket server in a separate thread"""
        try:
            # This function properly manages the event loop
            asyncio.run(self._run_websocket_server())
        except Exception as e:
            print(f"Error in WebSocket server thread: {e}")
            import traceback
            traceback.print_exc()
    async def _run_websocket_server(self):
        """The async function that runs the WebSocket server"""
        try:
            # Create a task that monitors the stop_event
            stop_monitor = asyncio.create_task(self._monitor_stop_event())
            
            # Create a task to process outgoing messages
            process_messages = asyncio.create_task(self._process_outgoing_messages())
            
            # Start WebSocket server
            async with websockets.serve(self._handle_client, "0.0.0.0", self.game_server.Port) as server:
                print(f"WebSocket server started successfully on port {self.game_server.Port}")
                
                # Wait for either the server to close or the stop event to be set
                # This allows us to exit cleanly when stop_event is set
                await stop_monitor
                
                # Cancel the message processing task
                process_messages.cancel()
                try:
                    await process_messages
                except asyncio.CancelledError:
                    pass
                
                print("WebSocket server stopped")
                
        except Exception as e:
            print(f"Error running WebSocket server: {e}")
            import traceback
            traceback.print_exc()
    
    async def _process_outgoing_messages(self):
        """Process outgoing messages from the queue"""
        while not self.stop_event.is_set():
            # Get any queued messages
            if self.game_server:
                messages = self.game_server.get_queued_messages()
                  # Process each message
                for msg_type, message, recipient in messages:
                    try:
                        if msg_type == "broadcast":
                            # Broadcast message to all clients
                            if self.game_server.ConnectedClients:
                                for player in self.game_server.ConnectedClients:
                                    try:
                                        await player.websocket.send(message)
                                        print(f"Broadcast message sent to {player.player_name}: {message}")
                                    except Exception as e:
                                        print(f"Error sending to {player.player_name}: {e}")
                        elif msg_type == "direct" and recipient:
                            # Send message to specific client
                            for player in self.game_server.ConnectedClients:
                                if player.websocket == recipient:
                                    try:
                                        await player.websocket.send(message)
                                        print(f"Direct message sent to {player.player_name}: {message}")
                                    except Exception as e:
                                        print(f"Error sending direct message: {e}")
                                    break
                    except Exception as e:
                        print(f"Error sending message: {e}")
            
            # Short delay to avoid busy waiting
            await asyncio.sleep(0.05)  # Check for new messages every 50ms
    
    async def _monitor_stop_event(self):
        """Monitor the stop event and return when it's set"""
        while not self.stop_event.is_set():
            await asyncio.sleep(0.1)  # Short sleep to avoid busy waiting
        return
    
    async def _handle_client(self, websocket):
        """Handle client websocket connections"""
        try:
            # Register client
            print(f"Client connected: {websocket.remote_address}")
            if self.game_server:
                # Add the client to the connected clients list in the game server
                player = self.game_server.add_client(websocket)

                # Send state change message to the client
                await websocket.send("SM-PlayingState")

                # Wait for a short time to allow the client to process the message
                await asyncio.sleep(0.1)

                # Send player object information
                await websocket.send(player.__str__())
            
            try:
                # Keep connection open and handle messages
                async for message in websocket:
                    try:
                        # Process incoming message
                        print(f"Received message: {message}")
                        
                        # Put message in queue for game processing
                        self.message_queue.put(message)
                        
                        # Echo the message back
                        #await websocket.send(f"Server received: {message}")
                        
                    except Exception as e:
                        print(f"Error processing message: {e}")
            
            except websockets.exceptions.ConnectionClosed:
                print(f"Connection closed with client: {websocket.remote_address}")
            
            finally:
                # Unregister client when connection is closed
                if self.game_server and websocket in self.game_server.ConnectedClients:
                    self.game_server.send_message("SM-MenuState", websocket)
                    self.game_server.remove_client(websocket)
        except Exception as e:
            print(f"Error in handle_client: {e}")
    
    async def broadcast_message(self, message):
        """Send a message to all connected clients"""
        try:
            if self.game_server and self.game_server.ConnectedClients:
                await asyncio.gather(
                    *[client.send(message) for client in self.game_server.ConnectedClients]
                )
        except Exception as e:
            print(f"Error broadcasting message: {e}")
    
    def stop(self):
        """Stop the WebSocket server"""
        if not self.is_running:
            return
            
        try:
            print("Signaling WebSocket server to stop...")
            # Signal the WebSocket server to stop by setting the stop event
            self.stop_event.set()
            
            # Wait briefly for thread to clean up
            if self.websocket_thread and self.websocket_thread.is_alive():
                print("Waiting for WebSocket server to terminate...")
                self.websocket_thread.join(2.0)  # Give it 2 seconds to terminate
            
            self.is_running = False
            self.websocket_thread = None
            print("WebSocket server stopped")
        except Exception as e:
            print(f"Error stopping WebSocket server: {e}")