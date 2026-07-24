"""screens/win.py – Win screen."""

import pygame

import settings as cfg
from game.states import GameState
from screens.common import result_screen


def run(screen: pygame.Surface, clock: pygame.time.Clock) -> GameState:
    return result_screen(screen, clock, "You Win!", cfg.GREEN)
