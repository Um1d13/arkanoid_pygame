"""Neon Breaker — entry point and screen flow.

Each non-gameplay screen (menu, high scores, end screen) is a small
function with its own local event loop; the actual level is played out
by src.game.Game, which owns the paddle/ball/brick simulation.
"""

import sys

import pygame

from src import config, scores, ui
from src.audio import SoundBank
from src.game import Game
from src.levels import available_levels
from src.sprites import Star


def _star_layer(count=90):
    return [Star() for _ in range(count)]


def _draw_starfield(screen, background, stars):
    screen.blit(background, (0, 0))
    for star in stars:
        star.update()
        star.draw(screen)


def menu_screen(screen, clock, background, stars):
    start_btn = ui.Button((config.WIDTH // 2 - 110, 360, 220, 54), "START")
    scores_btn = ui.Button((config.WIDTH // 2 - 110, 428, 220, 54), "HIGH SCORES")
    quit_btn = ui.Button((config.WIDTH // 2 - 110, 496, 220, 54), "QUIT")

    while True:
        mouse = pygame.mouse.get_pos()
        for btn in (start_btn, scores_btn, quit_btn):
            btn.update(mouse)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return "play"
            if start_btn.clicked(event):
                return "play"
            if scores_btn.clicked(event):
                return "high_scores"
            if quit_btn.clicked(event):
                return "quit"

        _draw_starfield(screen, background, stars)
        ui.draw_text(screen, "NEON BREAKER", 72, config.NEON_CYAN, (config.WIDTH // 2, 200), bold=True)
        ui.draw_text(screen, "an original arkanoid-style breakout", 22, config.DIM, (config.WIDTH // 2, 255))
        for btn in (start_btn, scores_btn, quit_btn):
            btn.draw(screen)
        ui.draw_text(screen, "Arrows/AD move  ·  SPACE launch  ·  X laser  ·  ESC pause", 18, config.DIM,
                      (config.WIDTH // 2, config.HEIGHT - 30))
        pygame.display.flip()
        clock.tick(config.FPS)


def high_scores_screen(screen, clock, background, stars):
    back_btn = ui.Button((config.WIDTH // 2 - 90, config.HEIGHT - 100, 180, 50), "BACK")
    entries = scores.load()

    while True:
        mouse = pygame.mouse.get_pos()
        back_btn.update(mouse)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_SPACE):
                return "menu"
            if back_btn.clicked(event):
                return "menu"

        _draw_starfield(screen, background, stars)
        ui.draw_text(screen, "HIGH SCORES", 52, config.NEON_YELLOW, (config.WIDTH // 2, 110), bold=True)
        if not entries:
            ui.draw_text(screen, "No scores yet — be the first!", 24, config.DIM, (config.WIDTH // 2, 220))
        for i, entry in enumerate(entries):
            y = 200 + i * 46
            ui.draw_text(screen, f"{i + 1}.", 28, config.DIM, (config.WIDTH // 2 - 120, y))
            ui.draw_text(screen, entry["name"], 28, config.WHITE, (config.WIDTH // 2, y), bold=True)
            ui.draw_text(screen, str(entry["score"]), 28, config.NEON_CYAN, (config.WIDTH // 2 + 120, y))
        back_btn.draw(screen)
        pygame.display.flip()
        clock.tick(config.FPS)


def end_screen(screen, clock, background, stars, title, title_color, final_score):
    entry_qualifies = scores.qualifies(final_score)
    initials = ""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if entry_qualifies:
                    if event.key == pygame.K_RETURN and initials:
                        scores.register(initials, final_score)
                        return "high_scores"
                    elif event.key == pygame.K_BACKSPACE:
                        initials = initials[:-1]
                    elif event.unicode.isalpha() and len(initials) < 3:
                        initials += event.unicode.upper()
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                    return "menu"

        _draw_starfield(screen, background, stars)
        ui.draw_text(screen, title, 64, title_color, (config.WIDTH // 2, 190), bold=True)
        ui.draw_text(screen, f"Final score: {final_score}", 30, config.WHITE, (config.WIDTH // 2, 260))

        if entry_qualifies:
            ui.draw_text(screen, "New high score! Enter initials:", 24, config.NEON_YELLOW, (config.WIDTH // 2, 340))
            box_text = (initials + "_" * (3 - len(initials)))
            ui.draw_text(screen, box_text, 46, config.NEON_CYAN, (config.WIDTH // 2, 390), bold=True)
            ui.draw_text(screen, "Press ENTER to save", 20, config.DIM, (config.WIDTH // 2, 440))
        else:
            ui.draw_text(screen, "Press SPACE to continue", 22, config.DIM, (config.WIDTH // 2, 380))

        pygame.display.flip()
        clock.tick(config.FPS)


def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        pass

    screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    pygame.display.set_caption(config.TITLE)
    clock = pygame.time.Clock()
    sounds = SoundBank()

    background = ui.vertical_gradient((config.WIDTH, config.HEIGHT), config.BG_TOP, config.BG_BOTTOM)
    stars = _star_layer()

    level_count = max(1, available_levels())
    state = "menu"
    level = 1
    score = 0
    lives = config.START_LIVES

    while True:
        if state == "menu":
            level, score, lives = 1, 0, config.START_LIVES
            state = menu_screen(screen, clock, background, stars)

        elif state == "high_scores":
            state = high_scores_screen(screen, clock, background, stars)

        elif state == "play":
            session = Game(screen, clock, sounds, level, score, lives)
            result, score = session.run()
            lives = session.lives
            if result == "quit":
                state = "quit"
            elif result == "game_over":
                state = "game_over"
            elif result == "level_clear":
                level += 1
                state = "victory" if level > level_count else "play"

        elif state == "game_over":
            state = end_screen(screen, clock, background, stars, "GAME OVER", config.NEON_PINK, score)

        elif state == "victory":
            sounds.win.play()
            state = end_screen(screen, clock, background, stars, "YOU WIN!", config.NEON_YELLOW, score)

        elif state == "quit":
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
