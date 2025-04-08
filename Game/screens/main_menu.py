import pygame
from screens.base_screen import BaseScreen
from screens.host_game import HostGameScreen

class MainMenuScreen(BaseScreen):
    """
    Main menu screen showing game options
    """
    def __init__(self, game_instance):
        super().__init__(game_instance)
        self.title_font = pygame.font.SysFont("Arial", 64, bold=True)
        self.menu_font = pygame.font.SysFont("Arial", 36)
        
        # Menu options
        self.options = ["Host Game", "Quit"]
        self.selected_option = 0
        
        # Colors
        self.title_color = (255, 255, 0)  # Yellow
        self.option_color = (255, 255, 255)  # White
        self.selected_color = (0, 255, 0)  # Green
        
        # Option rectangles for mouse interaction
        self.option_rects = []
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    self.select_option()
            elif event.type == pygame.MOUSEMOTION:
                # Check if mouse is over any option
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_option = i
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if any option was clicked
                if event.button == 1:  # Left mouse button
                    for i, rect in enumerate(self.option_rects):
                        if rect.collidepoint(event.pos):
                            self.selected_option = i
                            self.select_option()
                            break
    
    def select_option(self):
        if self.options[self.selected_option] == "Host Game":
            self.next_screen = HostGameScreen(self.game_instance)
        elif self.options[self.selected_option] == "Quit":
            self.game_instance.running = False
    
    def draw(self, screen):
        # Fill background
        screen.fill((0, 0, 0))
        
        # Draw title
        title_surface = self.title_font.render("Guitar Hero Game", True, self.title_color)
        title_rect = title_surface.get_rect(center=(self.game_instance.screen_width // 2, 100))
        screen.blit(title_surface, title_rect)
        
        # Reset option rectangles
        self.option_rects = []
        
        # Draw menu options
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.option_color
            option_surface = self.menu_font.render(option, True, color)
            option_rect = option_surface.get_rect(
                center=(self.game_instance.screen_width // 2, 250 + i * 60)
            )
            # Store rectangle for mouse interaction
            self.option_rects.append(option_rect)
            # Draw option text
            screen.blit(option_surface, option_rect)
            
            # Draw a button outline
            padding = 10
            button_rect = pygame.Rect(
                option_rect.left - padding,
                option_rect.top - padding,
                option_rect.width + (padding * 2),
                option_rect.height + (padding * 2)
            )
            pygame.draw.rect(screen, color, button_rect, 2, border_radius=5)