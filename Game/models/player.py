import random

class Player:
    websocket = None
    player_name = None
    score = 0

    def __init__(self, websocket):
        # Random list of animals
        animals = [
            "cat", "dog", "elephant", "giraffe", "lion", "tiger", "bear", "zebra", "snake", "monkey", "panda",
            "kangaroo", "koala", "whale", "dolphin", "shark", "octopus", "penguin", "flamingo", "parrot"]
        # Random list of colors
        colors = [
            "red", "blue", "green", "yellow", "purple", "orange", "pink", "brown", "black", "white", "gray", "cyan",
            "magenta", "lime", "navy", "teal", "maroon", "olive", "silver", "gold"]
        


        self.websocket = websocket
        self.player_name = f"{random.choice(colors)}-{random.choice(animals)}"
        self.score = 0

    def __str__(self):
        return f"PlayerObject \nPlayer={self.player_name} \nScore={self.score}"