"""game/states.py – Game Stats enum"""

from enum import IntEnum, auto


class GameState(IntEnum):
    MAIN_MENU = 0
    SETTINGS = auto()
    GAME = auto()
    WIN = auto()
    GAMEOVER = auto()
    QUIT = auto()
