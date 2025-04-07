import pygame
from screens.base_screen import BaseScreen
from screens.playing_game import PlayingGameScreen

class LobbyScreen(BaseScreen):
    """
    Lobby screen for when the game is hosted and waiting for players to join
    """
    def __init__(self, game_instance):
        super().__init__(game_instance)
        self.header_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 32)
        self.info_font = pygame.font.SysFont("Arial", 24)
        
        # Colors
        self.header_color = (255, 255, 0)  # Yellow
        self.text_color = (255, 255, 255)  # White
        self.active_color = (0, 255, 0)    # Green
        self.passive_color = (100, 100, 100)  # Gray
        self.highlight_color = (0, 255, 255)  # Cyan
        
        # Buttons
        self.start_rect = pygame.Rect(250, 350, 300, 50)
        self.back_rect = pygame.Rect(250, 420, 300, 50)
        
        # Refresh timer for player count
        self.refresh_timer = 0
        self.refresh_interval = 1000  # ms
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.start_game()
                elif event.key == pygame.K_ESCAPE:
                    self.go_back()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Check if start button was clicked
                    if self.start_rect.collidepoint(event.pos):
                        self.start_game()
                    # Check if back button was clicked
                    elif self.back_rect.collidepoint(event.pos):
                        self.go_back()
    
    def start_game(self):
        """Start the game with currently connected players"""
        self.next_screen = PlayingGameScreen(self.game_instance)
    
    def go_back(self):
        """Go back to the host game screen"""
        # Import here to avoid circular imports
        from screens.host_game import HostGameScreen
        self.next_screen = HostGameScreen(self.game_instance)
        # Note: This will keep the server running, but that's handled in the game_instance
    
    def update(self):
        """Update lobby information"""
        current_time = pygame.time.get_ticks()
        
        # Refresh the game state periodically
        if current_time - self.refresh_timer > self.refresh_interval:
            self.refresh_timer = current_time
            # Process any messages from clients
            self.game_instance.process_messages()
    
    def draw(self, screen):
        """Draw the lobby screen"""
        # Fill background
        screen.fill((0, 0, 0))
        
        # Draw header
        header_text = f"Lobby: {self.game_instance.game_server.GameName}"
        header_surface = self.header_font.render(header_text, True, self.header_color)
        header_rect = header_surface.get_rect(center=(self.game_instance.screen_width // 2, 80))
        screen.blit(header_surface, header_rect)
        
        # Draw server info
        ip_text = f"Server IP: {self.game_instance.game_server.HostIP}"
        ip_surface = self.text_font.render(ip_text, True, self.text_color)
        screen.blit(ip_surface, (50, 150))
        
        port_text = f"Port: {self.game_instance.game_server.Port}"
        port_surface = self.text_font.render(port_text, True, self.text_color)
        screen.blit(port_surface, (50, 190))
        
        # Draw player count with highlight
        player_count = len(self.game_instance.game_server.ConnectedClients)
        player_text = f"Connected Players: {player_count}"
        player_surface = self.text_font.render(player_text, True, self.highlight_color)
        screen.blit(player_surface, (50, 250))
        
        # Draw instructions
        if player_count == 0:
            instruction_text = "Waiting for players to join..."
        else:
            instruction_text = "Players connected! Ready to start game."
        
        instruction_surface = self.info_font.render(instruction_text, True, self.text_color)
        instruction_rect = instruction_surface.get_rect(center=(self.game_instance.screen_width // 2, 300))
        screen.blit(instruction_surface, instruction_rect)
        
        # Draw start button
        button_color = self.active_color if player_count > 0 else self.passive_color
        pygame.draw.rect(screen, button_color, self.start_rect, 2, border_radius=5)
        start_text = "Start Game" if player_count > 0 else "Waiting for Players..."
        start_surface = self.text_font.render(start_text, True, button_color)
        start_text_rect = start_surface.get_rect(center=self.start_rect.center)
        screen.blit(start_surface, start_text_rect)
        
        # Draw back button
        pygame.draw.rect(screen, self.passive_color, self.back_rect, 2, border_radius=5)
        back_surface = self.text_font.render("Back", True, self.text_color)
        back_text_rect = back_surface.get_rect(center=self.back_rect.center)
        screen.blit(back_surface, back_text_rect)