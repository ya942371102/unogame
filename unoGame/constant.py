from enum import Enum
from PIL import ImageTk
from PIL.Image import Image

PLAYER_VIEW_BACKGROUND = '#ffffff'
WINDOW_HEIGHT = 800
WINDOW_WIDTH = 1000
TOP_HEIGHT = 250
BOTTOM_HEIGHT = 300
LEFT_WIDTH = 350
RIGHT_WIDTH = 350
CARDS_CSV = 'images/cards.csv'
UNKNOWN_CARD_image_path = 'images/N.png'
CARD_HEIGHT = 150
CARD_WIDTH = 100


def init():
    global UNKNOWN_CARD
    UNKNOWN_CARD = ImageTk.PhotoImage(image=Image.open('images/N.png').resize(()))



