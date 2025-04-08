import pygame

class BaseScreen:
    """
    Base class for all game screens
    """
    def __init__(self, game_instance):
        self.game_instance = game_instance
        self.next_screen = None
        
    def handle_events(self, events):
        """Process pygame events"""
        pass
        
    def update(self):
        """Update screen logic"""
        pass
        
    def draw(self, screen):
        """Draw screen elements"""
        pass
        
    def get_next_screen(self):
        """Return the next screen to switch to, or None to stay on current screen"""
        return self.next_screen