"""main.py – main game entry"""

import pygame

import game.audio as audio
import settings as cfg
from game.states import GameState
from screens.game_screen import run as game_screen
from screens.gameover import run as gameover_screen
from screens.menu import run as menu_screen
from screens.settings import run as settings_screen
from screens.win import run as win_screen


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
    pygame.display.set_caption("Arkanoid")
    clock = pygame.time.Clock()
    audio.init_audio()

    state = GameState.MAIN_MENU
    level = 1

    while state != GameState.QUIT:
        if state == GameState.MAIN_MENU:
            state = menu_screen(screen, clock)
            if state == GameState.GAME:
                level = 1  # 
        elif state == GameState.SETTINGS:
            state = settings_screen(screen, clock)
        elif state == GameState.GAME:
            # TODO: increase level #
            state = game_screen(screen, clock, level)
        elif state == GameState.WIN:
            state = win_screen(screen, clock)
        elif state == GameState.GAMEOVER:
            state = gameover_screen(screen, clock)
        else:
            state = GameState.QUIT

    audio.stop_music()
    pygame.quit()


if __name__ == "__main__":
    main()
