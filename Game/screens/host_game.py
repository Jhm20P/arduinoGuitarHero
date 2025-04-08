import pygame
from screens.base_screen import BaseScreen
from screens.lobby_screen import LobbyScreen

class HostGameScreen(BaseScreen):
    """
    Screen for hosting a new game with a custom name
    """
    def __init__(self, game_instance):
        super().__init__(game_instance)
        self.header_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.text_font = pygame.font.SysFont("Arial", 32)
        self.input_font = pygame.font.SysFont("Arial", 36)
        
        # Game name input
        self.game_name = "My Guitar Hero Game"
        self.active_input = True
        self.input_rect = pygame.Rect(200, 250, 400, 50)
        
        # Colors
        self.header_color = (255, 255, 0)  # Yellow
        self.text_color = (255, 255, 255)  # White
        self.active_color = (0, 255, 0)    # Green
        self.passive_color = (100, 100, 100)  # Gray
        self.input_color = self.active_color
        self.current_color = self.text_color
        
        # Buttons
        self.start_rect = pygame.Rect(250, 350, 300, 50)
        self.back_rect = pygame.Rect(250, 420, 300, 50)
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if input box is clicked
                if self.input_rect.collidepoint(event.pos):
                    self.active_input = True
                    self.input_color = self.active_color
                else:
                    self.active_input = False
                    self.input_color = self.passive_color
                    
                # Check if start button is clicked
                if self.start_rect.collidepoint(event.pos):
                    self.start_game()
                    
                # Check if back button is clicked
                if self.back_rect.collidepoint(event.pos):
                    self.go_back()
                    
            if event.type == pygame.KEYDOWN:
                if self.active_input:
                    if event.key == pygame.K_BACKSPACE:
                        self.game_name = self.game_name[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.start_game()
                    else:
                        # Limit name length to prevent overflow
                        if len(self.game_name) < 25:  
                            self.game_name += event.unicode
    
    def start_game(self):
        # Create game server with custom name
        self.game_instance.create_game_server(self.game_name)
        # Transition to lobby screen instead of directly to playing screen
        self.next_screen = LobbyScreen(self.game_instance)
        
    def go_back(self):
        # Import here to avoid circular imports
        from screens.main_menu import MainMenuScreen
        self.next_screen = MainMenuScreen(self.game_instance)
    
    def draw(self, screen):
        # Fill background
        screen.fill((0, 0, 0))
        
        # Draw header
        header_surface = self.header_font.render("Host a New Game", True, self.header_color)
        header_rect = header_surface.get_rect(center=(self.game_instance.screen_width // 2, 100))
        screen.blit(header_surface, header_rect)
        
        # Draw input label
        label_surface = self.text_font.render("Game Name:", True, self.text_color)
        screen.blit(label_surface, (self.input_rect.x, self.input_rect.y - 40))
        
        # Draw input box
        pygame.draw.rect(screen, self.input_color, self.input_rect, 2)
        input_surface = self.input_font.render(self.game_name, True, self.text_color)
        screen.blit(input_surface, (self.input_rect.x + 5, self.input_rect.y + 10))
        
        # Draw start button
        pygame.draw.rect(screen, self.active_color, self.start_rect, 2)
        start_surface = self.text_font.render("Start Game", True, self.text_color)
        start_text_rect = start_surface.get_rect(center=self.start_rect.center)
        screen.blit(start_surface, start_text_rect)
        
        # Draw back button
        pygame.draw.rect(screen, self.passive_color, self.back_rect, 2)
        back_surface = self.text_font.render("Back to Menu", True, self.text_color)
        back_text_rect = back_surface.get_rect(center=self.back_rect.center)
        screen.blit(back_surface, back_text_rect)