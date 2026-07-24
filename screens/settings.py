"""screens/settings.py – Settings Screen."""

import pygame

import game.audio as audio
import settings as cfg
from game.states import GameState
from screens.common import draw_button


def run(screen: pygame.Surface, clock: pygame.time.Clock) -> GameState:
    title_font = pygame.font.Font(None, 48)
    button_font = pygame.font.Font(None, 36)

    back_btn = pygame.Rect(50, 500, 150, 50)
    toggle_btn = pygame.Rect(300, 250, 200, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameState.QUIT
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_btn.collidepoint(event.pos):
                    return GameState.MAIN_MENU
                if toggle_btn.collidepoint(event.pos):
                    audio.toggle_sound()
                    audio.play_sound(audio.hit_sound)  # Sound Check

        screen.fill(cfg.BLACK)
        title = title_font.render("Settings", True, cfg.WHITE)
        screen.blit(title, title.get_rect(centerx=cfg.WIDTH // 2, y=100))

        sound_text = "Sound: ON" if audio.sound_enabled else "Sound: OFF"
        draw_button(screen, toggle_btn, sound_text, button_font)
        draw_button(screen, back_btn, "Back", button_font)

        pygame.display.flip()
        clock.tick(cfg.FPS)
