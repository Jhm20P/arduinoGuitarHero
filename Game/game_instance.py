import pygame
import os
import random
from models.game_server import GameServer
from networking.network_manager import NetworkManager

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
        self.network_manager = NetworkManager()
        
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
            # Create game server object
            self.game_server = GameServer(game_name)
            
            # Start network services
            self.network_manager.start_services(self.game_server)
            
            print(f"Game server created: {game_name}")
            print(f"Server running at: {self.game_server.HostIP}:{self.game_server.Port}")
            print(f"HTTP discovery service running at: http://{self.game_server.HostIP}:{self.network_manager.http_port}/guitargame")
        except Exception as e:
            print(f"Error creating game server: {e}")
            import traceback
            traceback.print_exc()
    
    def process_messages(self):
        """Process game messages from controllers"""
        # Get messages from network manager
        messages = self.network_manager.process_messages()
        
        # Process each message
        for message in messages:
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
                print(f"Error processing message: {e}")
    
    def stop_server(self):
        """Stop the game server and all networking services"""
        # Stop all network services
        if self.network_manager:
            self.network_manager.stop_services()
            
        # Reset game server
        self.game_server = None
        print("Server shutdown completed")
    
    def get_random_midi_file(self):
        """Get a random MIDI file from the music directory"""
        try:
            # Get the directory of the current script
            base_dir = os.path.dirname(os.path.abspath(__file__))
            music_dir = os.path.join(base_dir, 'music')
            
            # Check if music directory exists
            if not os.path.exists(music_dir):
                print(f"Music directory not found: {music_dir}")
                return None
            
            # Get all MIDI files (.mid or .midi extensions)
            midi_files = [f for f in os.listdir(music_dir) 
                         if f.lower().endswith(('.mid', '.midi'))]
            
            # Check if any MIDI files were found
            if not midi_files:
                print("No MIDI files found in the music directory")
                return None
            
            # Select a random MIDI file
            random_midi = random.choice(midi_files)
            midi_path = os.path.join(music_dir, random_midi)
            
            print(f"Selected random MIDI file: {random_midi}")
            return midi_path
            
        except Exception as e:
            print(f"Error loading random MIDI file: {e}")
            import traceback
            traceback.print_exc()
            return None

if __name__ == "__main__":
    game = GameInstance()
    game.start()