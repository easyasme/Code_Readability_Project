"""
Teyeliz - Player Class
"""

# Import Python modules
import pygame

# Import game modules
from data.card import Card

# Player class
class Player():
    # Constructor
    def __init__(self, s=None, pygame_data=None):
        # If socket is not specified, assign 0 (server)
        if s is None:
            s = 0

        # Assign the player's socket type (0 = server, 1 = client)
        self.socket = s

        # Initialize player's hand and tic-tac-toe grid
        self.hand = [Card() for i in range(5)]
        self.tictactoe = [[0, 0, 0],
                          [0, 0, 0],
                          [0, 0, 0]]

        # Receive pygame data
        self.pygame_data = pygame_data

    # Function to play a card
    def play_card(self, position):
        # Get the card to play
        card = self.hand[position]

        # Save card data
        element = card.element
        color = card.color
        power = card.power

        data = (element, color, power)

        # Remove the card from the hand
        self.hand[position] = None

        # Show an empty card on the pygame window
        empty_card_image = pygame.image.load("resources/graphics/cards/empty.png")
        empty_card_image = pygame.transform.scale(empty_card_image, (64, 104))
        empty_card_image_rect = empty_card_image.get_rect()
        empty_card_image_rect.topleft = (138 + (106 * position), 259)
        self.pygame_data[1].blit(empty_card_image, empty_card_image_rect)

        # Show the played card on the pygame window
        card_image = card.image
        card_image = pygame.transform.scale(card_image, (96, 156))
        card_image_rect = card_image.get_rect()
        if self.socket == 0:
            card_image_rect.topleft = (254, 60)
        else:
            card_image_rect.topleft = (410, 60)
        self.pygame_data[1].blit(card_image, card_image_rect)

        # Update the pygame window
        self.pygame_data[0].flip()

        return data

    # Function to draw a new card
    def draw_card(self, position):
        self.hand[position] = Card()

    # Function to add a card to the tic-tac-toe grid
    def add_card_to_tictactoe(self, data):
        element = data[0]
        color = data[1]

        self.tictactoe[element - 1][color - 1] = 1

    # Function to check if the player wins the game
    def check_tictactoe(self):
        # Check if the player fills a row of the grid
        for i in range(3):
            if self.tictactoe[i][0] == self.tictactoe[i][1] == self.tictactoe[i][2] == 1:
                return True

        # Check if the player fills a column of the grid
        for j in range(3):
            if self.tictactoe[0][j] == self.tictactoe[1][j] == self.tictactoe[2][j] == 1:
                return True

        return False

    # Function to show the player's hand
    def show_hand(self):
        # Show the cards on the pygame window
        for i in range(5):
            card = self.hand[i]
            card_image = card.image
            card_image = pygame.transform.scale(card_image, (64, 104))
            card_image_rect = card_image.get_rect()
            card_image_rect.topleft = (138 + (106 * i), 259)
            self.pygame_data[1].blit(card_image, card_image_rect)
        
        # Update the pygame window
        self.pygame_data[0].flip()

    # Function to show the player's tic-tac-toe grid
    def show_tictactoe(self):
        # List of elements and colors
        element = ["Tletl", "Atl", "Metl"]
        color = ["Pink", "Turquoise", "Gold"]

        for i in range(3):
            for j in range(3):
                # If the cell is not empty, show the card thumbnail
                if self.tictactoe[i][j] == 1:
                    thumbnail = pygame.image.load(f"resources/graphics/thumbnails/{element[i]}/{element[i]}{color[j]}.png")
                    thumbnail = pygame.transform.scale(thumbnail, (32, 32))
                    thumbnail_rect = thumbnail.get_rect()
                    if self.socket == 0:
                        thumbnail_rect.topleft = (73 + (50 * j), 72 + (50 * i))
                    else:
                        thumbnail_rect.topleft = (556 + (50 * j), 72 + (50 * i))
                    self.pygame_data[1].blit(thumbnail, thumbnail_rect)

        # Update the pygame window
        self.pygame_data[0].flip()

    # Define the string method of the class
    def __str__(self):
        if self.socket == 0:
            return "Server"
        else:
            return "Client"

    # Define the representation method of the class
    def __repr__(self):
        return self.__str__()
