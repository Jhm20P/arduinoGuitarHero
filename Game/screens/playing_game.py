import pygame
import mido
import time
from screens.base_screen import BaseScreen

class PlayingGameScreen(BaseScreen):
    """
    Screen for the actual gameplay
    """
    def __init__(self, game_instance):
        super().__init__(game_instance)
        self.font = pygame.font.SysFont("Arial", 36)
        self.header_font = pygame.font.SysFont("Arial", 48, bold=True)
        
        # Guitar Hero gameplay elements
        self.track_width = 100
        self.track_spacing = 20
        self.num_tracks = 4
        self.note_speed = 5
        self.notes = []  # List of notes currently on screen
        
        # MIDI file playing
        self.midi_file = self.game_instance.get_random_midi_file()
        self.midi_track = None
        self.midi_events = []
        self.current_event_index = 0
        self.last_note_time = 0
        self.start_time = time.time()
        self.load_midi()
        
        # Colors
        self.track_colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (255, 255, 0),  # Yellow
            (0, 0, 255)     # Blue
        ]
        self.header_color = (255, 255, 0)  # Yellow
        self.text_color = (255, 255, 255)  # White
        self.button_color = (100, 100, 100)  # Gray
        
        # Game stats
        self.score = 0
        self.combo = 0
        
        # Track the currently playing song name
        self.song_name = "No song loaded"
        if self.midi_file:
            # Extract just the filename without path and extension
            import os
            self.song_name = os.path.basename(self.midi_file)
            self.song_name = os.path.splitext(self.song_name)[0]
        
        # Back button
        self.back_button_rect = pygame.Rect(20, 540, 150, 40)

        # Broadcast game start message to all clients
        if (self.game_instance and 
            hasattr(self.game_instance, 'game_server') and 
            self.game_instance.game_server and 
            hasattr(self.game_instance.game_server, 'outgoing_message_queue')):
            
            # Format: "Game-Start"
            message = f"Game-Start"
            
            # Use the broadcast_message method from GameServer
            self.game_instance.game_server.broadcast_message(message)

    def load_midi(self):
        """Load and prepare the MIDI file for playing"""
        if not self.midi_file:
            print("No MIDI file available to load")
            return
        try:
            # Load the MIDI file
            midi = mido.MidiFile(self.midi_file)
            
            # Find the first track with note events
            self.midi_events = []
            
            # Extract note_on events with velocity > 0
            raw_events = []
            for msg in midi:
                if not msg.is_meta and msg.type == 'note_on' and msg.velocity > 0:
                    raw_events.append(msg)
            
            # Convert delta times to absolute times
            # MIDI files store delta times (time since the last event)
            absolute_time = 0
            for msg in raw_events:
                absolute_time += msg.time
                # Create a copy of the message with absolute timestamp
                copied_msg = msg.copy(time=absolute_time)
                self.midi_events.append(copied_msg)
            
            # Sort by absolute time (should already be sorted, but just to be safe)
            self.midi_events.sort(key=lambda x: x.time)
            
            # Scale the timings to make gameplay smoother
            # First, determine the tempo scaling factor
            if len(self.midi_events) > 1:
                # Calculate a reasonable scaling factor based on song length
                total_duration = self.midi_events[-1].time
                # We want the whole song to take about 2-3 minutes to play
                target_duration = 120  # seconds
                self.tempo_scale = target_duration / total_duration
                
                # Add spacing between notes that are too close together
                min_time_between_notes = 0.5  # minimum seconds between consecutive notes
                
                # Apply scaling and enforce minimum spacing
                last_time = 0
                for i, msg in enumerate(self.midi_events):
                    # Scale the time
                    scaled_time = msg.time * self.tempo_scale
                    
                    # Enforce minimum spacing
                    if i > 0 and scaled_time - last_time < min_time_between_notes:
                        scaled_time = last_time + min_time_between_notes
                    
                    # Update the message time and track the last time
                    self.midi_events[i] = msg.copy(time=scaled_time)
                    last_time = scaled_time
            else:
                # Default scaling if we don't have enough events
                self.tempo_scale = 1.0
            
            # Convert note pitch to track number (map the range of notes to 4 tracks)
            note_min = min([msg.note for msg in self.midi_events]) if self.midi_events else 60
            note_max = max([msg.note for msg in self.midi_events]) if self.midi_events else 72
            note_range = max(note_max - note_min, 1)
            
            # Create track mapping for each note
            self.track_mapping = {}
            for i, msg in enumerate(self.midi_events):
                # Map the note to one of the 4 tracks
                track = min(int((msg.note - note_min) * self.num_tracks / note_range), self.num_tracks - 1)
                self.track_mapping[i] = track
            
            # Add initial delay to give player time to prepare
            self.start_time = time.time() + 3.0  # 3 second delay before notes start
            
            print(f"Loaded MIDI file with {len(self.midi_events)} note events")
            print(f"Song duration: {self.midi_events[-1].time:.1f} seconds (after scaling)")
            
        except Exception as e:
            print(f"Error loading MIDI file: {e}")
            import traceback
            traceback.print_exc()
            self.midi_events = []
            
        except Exception as e:
            print(f"Error loading MIDI file: {e}")
            import traceback
            traceback.print_exc()
            self.midi_events = []

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.go_back()
                    
                # Handle key presses for gameplay
                self.handle_gameplay_input(event.key)
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Check if back button was clicked
                    if self.back_button_rect.collidepoint(event.pos):
                        self.go_back()
    
    def go_back(self):
        """Go back to the lobby screen"""
        # Broadcast game end message to all clients
        if (self.game_instance and 
            hasattr(self.game_instance, 'game_server') and 
            self.game_instance.game_server and 
            hasattr(self.game_instance.game_server, 'outgoing_message_queue')):
            
            # Format: "Game-End"
            message = f"Game-End"
            
            # Use the broadcast_message method from GameServer
            self.game_instance.game_server.broadcast_message(message)
        # Import here to avoid circular imports
        from screens.lobby_screen import LobbyScreen
        self.next_screen = LobbyScreen(self.game_instance)
        
    def handle_gameplay_input(self, key):
        """Handle gameplay inputs - will be integrated with controller data"""
        key_map = {
            pygame.K_a: 0,  # First track
            pygame.K_s: 1,  # Second track
            pygame.K_d: 2,  # Third track
            pygame.K_f: 3   # Fourth track
        }
        
        if key in key_map:
            track = key_map[key]
            self.check_note_hit(track)
    
    def check_note_hit(self, track):
        """Check if a note was hit successfully"""
        hit_zone_y = self.game_instance.screen_height - 100
        hit_zone_height = 30
        
        # Check if any note is in the hit zone for this track
        for note in self.notes[:]:
            if note['track'] == track and \
               hit_zone_y - hit_zone_height/2 <= note['y'] <= hit_zone_y + hit_zone_height/2:
                # Note hit!
                self.score += 100 * (self.combo + 1)
                self.combo += 1
                self.notes.remove(note)
                return
                
        # Note missed or wrong track
        self.combo = 0
    def update(self):
        # Move existing notes down
        for note in self.notes[:]:
            note['y'] += self.note_speed
            
            # Remove notes that have gone off screen
            if note['y'] > self.game_instance.screen_height:
                self.notes.remove(note)
                self.combo = 0  # Missed note
                
        # Randomly generate new notes based on connected client inputs
        # For now, just check if we need to process incoming messages
        self.game_instance.process_messages()
        
        # Generate notes from MIDI events
        current_time = time.time() - self.start_time
        while self.current_event_index < len(self.midi_events) and self.midi_events[self.current_event_index].time <= current_time:
            # Use the track mapping instead of directly accessing the track attribute
            track = self.track_mapping.get(self.current_event_index, 0)
            self.add_note(track)
            self.current_event_index += 1    
    def add_note(self, track):
        """Add a new note to the specified track"""
        if 0 <= track < self.num_tracks:
            # Calculate time until note needs to be hit
            # Distance from top to hit zone divided by note speed gives us the time
            hit_zone_y = self.game_instance.screen_height - 100
            time_to_hit = hit_zone_y / self.note_speed  # Time in frames
            # Convert to milliseconds (assuming 60 fps)
            time_to_hit_ms = int(time_to_hit * 1000 / 60)

            # Calculate the time when the note hits the hit zone since the start of the song in ms
            note_time = self.midi_events[self.current_event_index].time * 1000 * self.tempo_scale

            
            # Add note to the game
            self.notes.append({
                'track': track,
                'y': 0
            })
            
            try:
                # Only attempt to send messages if we have a valid server with the queue attribute
                if (self.game_instance and 
                    hasattr(self.game_instance, 'game_server') and 
                    self.game_instance.game_server and 
                    hasattr(self.game_instance.game_server, 'outgoing_message_queue')):
                    
                    # Format: "NOTE-{track}-{time_in_ms}"
                    message = f"NOTE-{track}-{note_time}"
                    
                    # Use the broadcast_message method from GameServer
                    self.game_instance.game_server.broadcast_message(message)
            except Exception as e:
                # Just log the error but don't crash the game
                print(f"Error sending note message: {e}")
                # Game can continue even if messages fail to send
    
    def draw(self, screen):
        # Fill background
        screen.fill((0, 0, 0))
        
        # Draw game name
        name_surface = self.header_font.render(f"Game: {self.game_instance.game_server.GameName}", True, self.header_color)
        screen.blit(name_surface, (20, 20))
        
        # Draw connected clients
        clients_surface = self.font.render(f"Connected Players: {len(self.game_instance.game_server.ConnectedClients)}", True, self.text_color)
        screen.blit(clients_surface, (20, 160))

        # Draw player names
        player_names = [player.player_name for player in self.game_instance.game_server.ConnectedClients]
        player_names_surface = self.font.render(", ".join(player_names), True, self.text_color)
        screen.blit(player_names_surface, (20, 200))
        
        # Draw song name
        song_surface = self.font.render(f"Song: {self.song_name}", True, self.text_color)
        screen.blit(song_surface, (20, 240))
        
        # Calculate track positions
        total_width = (self.track_width * self.num_tracks) + (self.track_spacing * (self.num_tracks - 1))
        start_x = (self.game_instance.screen_width - total_width) // 2
        
        # Draw tracks
        for i in range(self.num_tracks):
            track_x = start_x + (i * (self.track_width + self.track_spacing))
            
            # Draw track
            pygame.draw.rect(
                screen, 
                self.track_colors[i],
                (track_x, 0, self.track_width, self.game_instance.screen_height),
                2
            )
            
            # Draw hit zone
            hit_zone_y = self.game_instance.screen_height - 100
            pygame.draw.rect(
                screen,
                self.track_colors[i],
                (track_x, hit_zone_y - 15, self.track_width, 30)
            )
        
        # Draw notes
        for note in self.notes:
            track_x = start_x + (note['track'] * (self.track_width + self.track_spacing))
            pygame.draw.rect(
                screen,
                self.track_colors[note['track']],
                (track_x, note['y'] - 15, self.track_width, 30)
            )
        
        # Draw back button
        pygame.draw.rect(screen, self.button_color, self.back_button_rect, 2, border_radius=5)
        back_text = self.font.render("Back", True, self.text_color)
        back_text_rect = back_text.get_rect(center=self.back_button_rect.center)
        screen.blit(back_text, back_text_rect)