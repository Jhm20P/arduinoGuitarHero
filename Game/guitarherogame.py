import asyncio
import websockets
import pygame
import json
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading


class GameServer:
    HostName = socket.gethostname()
    HostIP = socket.gethostbyname(HostName)
    Port = 8765


# Configuration for the WebSocket server
HOST = "0.0.0.0"  # Listen on all available interfaces
PORT = 8765       # Port number

# Store connected clients
connected_clients = set()

# Function to get the local IP address of the server


def get_local_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

# HTTP request handler for service discovery


class ServiceDiscoveryHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/guitargame":
            # Respond with local IP and port
            response = json.dumps({"ip": get_local_ip(), "port": PORT})
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response.encode())
            print(f"Responded to HTTP service discovery with: {response}")
        else:
            self.send_response(404)
            self.end_headers()

# Function to start the HTTP server


def start_http_server():
    http_server = HTTPServer((HOST, 80), ServiceDiscoveryHandler)
    print(f"HTTP server for service discovery started on http://{HOST}:8080")
    http_server.serve_forever()

# Handle client connections for the "/guitargame" endpoint


async def handle_service_discovery(websocket):
    path = websocket
    if path == "/guitargame":
        try:
            # Respond with local IP and port
            response = json.dumps({"ip": get_local_ip(), "port": PORT})
            await websocket.send(response)
            print(f"Responded to service discovery with: {response}")
        except Exception as e:
            print(f"Error in service discovery: {e}")
    else:
        # Fallback to the main client handler for other paths
        await handle_client(websocket)

# Handle client connections


async def handle_client(websocket):
    # Register client
    print(f"Client connected: {websocket.remote_address}")
    connected_clients.add(websocket)

    try:
        # Keep connection open and handle messages
        async for message in websocket:
            try:
                # Process incoming message
                data = message
                print(f"Received message: {data}")

                # Example: Echo the message back
                await websocket.send(f"Server received: {data}")

                # You can parse JSON if Arduino sends structured data
                # json_data = json.loads(data)
                # process_data(json_data)

            except Exception as e:
                print(f"Error processing message: {e}")

    except websockets.exceptions.ConnectionClosed:
        print(f"Connection closed with client: {websocket.remote_address}")

    finally:
        # Unregister client when connection is closed
        connected_clients.remove(websocket)

# Function to send a message to all connected clients


async def broadcast_message(message):
    if connected_clients:
        await asyncio.gather(
            *[client.send(message) for client in connected_clients]
        )

# Main function to start both WebSocket and HTTP servers


async def main():
    # Start HTTP server in a separate thread
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()

    # Start WebSocket server
    server = await websockets.serve(handle_client, HOST, PORT)
    print(f"WebSocket server started on ws://{HOST}:{PORT}")

    # Keep the server running
    await server.wait_closed()

# Run the server
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped by user")
