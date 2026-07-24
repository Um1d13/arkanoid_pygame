"""screens/gameover.py – Game Over Screen."""

import pygame

import settings as cfg
from game.states import GameState
from screens.common import result_screen


def run(screen: pygame.Surface, clock: pygame.time.Clock) -> GameState:
    return result_screen(screen, clock, "GAME OVER", cfg.RED)
