from enum import Enum, auto
import pygame

# Game Parameters
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CAPTION = "Wumpus World"
FPS = 10

# Colors
WHITE = "#FFFFFF"
BLACK = "#000000"
DARK_GRAY = "##424242"
LIGHT_GRAY = "#D3D3D3"
RED = "#732727"
BLUE = "#273D73"

# Fonts
FONT_TITLE = "input/fonts/Barbra.ttf"
TITLE_SIZE = 80
FONT_TEXT = "input/fonts/Kanit.ttf"
BUTTON_SIZE = 50
TEXT_SIZE = 30


# Maps
MAP_LIST = [
    "input/maps/map1.txt",
    "input/maps/map2.txt",
    "input/maps/map3.txt",
    "input/maps/map4.txt",
    "input/maps/map5.txt",
]

# Output
OUTPUT_LIST = [
    "output/output1.txt",
    "output/output2.txt",
    "output/output3.txt",
    "output/output4.txt",
    "output/output5.txt",
]

# Assets
IMG_UNDISCOVERED_CELL = "input/assets/undiscovered_cell.png"
IMG_DISCOVERED_CELL = "input/assets/discovered_cell.png"
IMG_PIT = "input/assets/pit.png"
IMG_AGENT_RIGHT = "input/assets/agent_right.png"
IMG_AGENT_LEFT = "input/assets/agent_left.png"
IMG_AGENT_UP = "input/assets/agent_up.png"
IMG_AGENT_DOWN = "input/assets/agent_down.png"
IMG_WUMPUS = "input/assets/wumpus.png"
IMG_GOLD = "input/assets/gold.png"
IMG_POISONOUS_GAS = "input/assets/poisonous_gas.png"
IMG_HEALING_POTIONS = "input/assets/healing_potions.png"
IMG_STENCH = "input/assets/stench.png"
IMG_BREEZE = "input/assets/breeze.png"
IMG_SCREAM = "input/assets/wumpus_scream.png"
IMG_WHIFF = "input/assets/whiff.png"
IMG_GLOW = "input/assets/glow.png"
IMG_ARROW_UP = "input/assets/arrow_up.png"
IMG_ARROW_DOWN = "input/assets/arrow_down.png"
IMG_ARROW_LEFT = "input/assets/arrow_left.png"
IMG_ARROW_RIGHT = "input/assets/arrow_right.png"
IMG_GAMEOVER = "input/assets/game_over.png"
IMG_WIN = "input/assets/win_game.png"


# Cell Types
class CellType(Enum):
    UNDISCOVERED = auto()
    DISCOVERED = auto()
    PIT = auto()


# Objects
class Object(Enum):
    EMPTY = "-"
    WUMPUS = "W"
    PIT = "P"
    AGENT = "A"
    GOLD = "G"
    POISONOUS_GAS = "P_G"
    HEALING_POTIONS = "H_P"
    STENCH = "S"
    BREEZE = "B"
    WHIFF = "W_H"
    GLOW = "G_L"
    SCREAM = "S_C"


# Actions
class Action(Enum):
    MOVE_FORWARD = auto()
    TURN_LEFT = auto()
    TURN_RIGHT = auto()
    SHOOT = auto()
    GRAB_G = auto()
    GRAB_HP = auto()


# Directions
class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()