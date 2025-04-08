"""
HTTP Server for Guitar Hero Game discovery service
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class GameDiscoveryServer:
    """
    Handles HTTP requests for game discovery
    """
    def __init__(self, game_server, port=8080):
        self.game_server = game_server
        self.port = port
        self.http_server = None
        self.http_thread = None
        self.is_running = False
        
    def start(self):
        """Start the HTTP server for game discovery"""
        if self.is_running:
            print("HTTP server already running")
            return
            
        try:
            # Create custom request handler with access to the game server
            server_instance = self
            
            class CustomHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    try:
                        if self.path == "/guitargame":
                            if server_instance.game_server:
                                response = json.dumps(server_instance.game_server.to_dict())
                                self.send_response(200)
                                self.send_header("Content-Type", "application/json")
                                self.end_headers()
                                self.wfile.write(response.encode())
                                print(f"Responded to HTTP service discovery with: {response}")
                            else:
                                self.send_response(503)  # Service Unavailable
                                self.end_headers()
                        else:
                            self.send_response(404)
                            self.end_headers()
                    except Exception as e:
                        print(f"Error in HTTP handler: {e}")
                
                def log_message(self, format, *args):
                    # Suppress noisy HTTP server logs
                    pass
            
            # Use a non-privileged port that doesn't require admin rights
            server_address = ("0.0.0.0", self.port)
            self.http_server = HTTPServer(server_address, CustomHandler)
            self.is_running = True
            
            # Start server in a separate thread
            self.http_thread = threading.Thread(target=self._server_thread, daemon=True)
            self.http_thread.start()
            
            print(f"HTTP server for service discovery started on http://0.0.0.0:{self.port}")
        except Exception as e:
            print(f"Error starting HTTP server: {e}")
            import traceback
            traceback.print_exc()
    
    def _server_thread(self):
        """Thread function for running the HTTP server"""
        try:
            self.http_server.serve_forever()
        except Exception as e:
            print(f"HTTP server thread error: {e}")
    
    def stop(self):
        """Stop the HTTP server"""
        if not self.is_running:
            return
            
        try:
            print("Shutting down HTTP server...")
            if self.http_server:
                # Use a separate thread to shutdown HTTP server to avoid blocking
                shutdown_thread = threading.Thread(target=self._shutdown_http_server, daemon=True)
                shutdown_thread.start()
                shutdown_thread.join(1.0)  # Wait for up to 1 second
            
            self.is_running = False
            self.http_server = None
            self.http_thread = None
            print("HTTP server shut down successfully")
        except Exception as e:
            print(f"Error stopping HTTP server: {e}")
    
    def _shutdown_http_server(self):
        """Helper method to shut down HTTP server without blocking"""
        try:
            if self.http_server:
                self.http_server.shutdown()
                self.http_server.server_close()
        except Exception as e:
            print(f"Error in HTTP server shutdown: {e}")