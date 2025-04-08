import pygame
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
        
        # Back button
        self.back_button_rect = pygame.Rect(20, 540, 150, 40)
        
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
        # Import here to avoid circular imports
        from screens.main_menu import MainMenuScreen
        self.next_screen = MainMenuScreen(self.game_instance)
        
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
        
    def add_note(self, track):
        """Add a new note to the specified track"""
        if 0 <= track < self.num_tracks:
            self.notes.append({
                'track': track,
                'y': 0
            })
    
    def draw(self, screen):
        # Fill background
        screen.fill((0, 0, 0))
        
        # Draw game name
        name_surface = self.header_font.render(f"Game: {self.game_instance.game_server.GameName}", True, self.header_color)
        screen.blit(name_surface, (20, 20))
        
        # Draw score
        score_surface = self.font.render(f"Score: {self.score}", True, self.text_color)
        screen.blit(score_surface, (20, 80))
        
        # Draw combo
        combo_surface = self.font.render(f"Combo: {self.combo}", True, self.text_color)
        screen.blit(combo_surface, (20, 120))
        
        # Draw connected clients
        clients_surface = self.font.render(f"Connected Players: {len(self.game_instance.game_server.ConnectedClients)}", True, self.text_color)
        screen.blit(clients_surface, (20, 160))
        
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