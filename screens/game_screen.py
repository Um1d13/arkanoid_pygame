"""screens/game_screen.py – main game screen.

Contains all the game logic and physics
"""

import pygame

import game.audio as audio
import settings as cfg
from game.entities import Ball, Bonus, Brick, LaserBullet, Paddle
from game.level import load_level
from game.particles import Particle, draw_particles, spawn_burst, update_particles
from game.states import GameState

LASER_COOLDOWN = 300 # msec


def _new_ball(paddle: Paddle) -> Ball:
    return Ball(paddle.rect.centerx, paddle.rect.top - cfg.BALL_RADIUS)


def _bounce_off_rect(ball: Ball, rect: pygame.Rect) -> None:
    """Bounces off the ball form the given rect."""
    overlap_left = ball.rect.right - rect.left
    overlap_right = rect.right - ball.rect.left
    overlap_top = ball.rect.bottom - rect.top
    overlap_bottom = rect.bottom - ball.rect.top

    min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
    if min_overlap == overlap_top and ball.vy > 0:
        ball.rect.bottom = rect.top
        ball.vy *= -1
    elif min_overlap == overlap_bottom and ball.vy < 0:
        ball.rect.top = rect.bottom
        ball.vy *= -1
    elif min_overlap == overlap_left and ball.vx > 0:
        ball.rect.right = rect.left
        ball.vx *= -1
    elif min_overlap == overlap_right and ball.vx < 0:
        ball.rect.left = rect.right
        ball.vx *= -1


def _handle_ball_vs_paddle(ball: Ball, paddle: Paddle) -> None:
    """Bounces the ball from the Paddle."""
    _bounce_off_rect(ball, paddle.rect)
    offset = (ball.rect.centerx - paddle.rect.centerx) / (paddle.rect.width / 2)
    max_vx = cfg.MAX_BALL_SPEED_X
    ball.vx = max(-max_vx, min(max_vx, offset * max_vx))


def _handle_ball_vs_bricks(
    ball: Ball,
    bricks: list[Brick],
    bonuses: list[Bonus],
    particles: list[Particle],
) -> int:
    """Handles the ball bouncong off the bricks. Returns score"""
    scored = 0
    for brick in bricks[:]:
        if not ball.rect.colliderect(brick.rect):
            continue
        _bounce_off_rect(ball, brick.rect)
        if brick.hp == -1:  # indestructable
            continue
        bonus_type = brick.hit()
        audio.play_sound(audio.hit_sound)
        if brick.hp <= 0:  # The brick is destroyed
            bricks.remove(brick)
            scored += 10
            spawn_burst(particles, brick.rect.center, brick.color)
            if bonus_type:
                bonuses.append(Bonus(brick.rect.center, bonus_type))
    return scored


def _update_balls(
    balls: list[Ball],
    paddle: Paddle,
    bricks: list[Brick],
    bonuses: list[Bonus],
    particles: list[Particle],
) -> int:
    """ Updates all the balls, returns score."""
    scored = 0
    for ball in balls[:]:
        ball.update()
        if ball.rect.colliderect(paddle.rect) and ball.vy > 0:
            _handle_ball_vs_paddle(ball, paddle)
        scored += _handle_ball_vs_bricks(ball, bricks, bonuses, particles)
        if ball.rect.top > cfg.HEIGHT:  # Life is lost
            balls.remove(ball)
    return scored


def _apply_bonus(bonus_type: str, paddle: Paddle, balls: list[Ball], lives: int) -> int:
    """ Applies the bonus effect """
    if bonus_type == "extend":
        paddle.extend()
    elif bonus_type == "multiball":
        balls.append(_new_ball(paddle))
    elif bonus_type == "laser":
        paddle.laser = True
    elif bonus_type == "extra_life":
        lives += 1
    elif bonus_type == "shrink":
        paddle.narrow()
    elif bonus_type == "speed_up":
        for ball in balls:
            ball.speed_up()
    elif bonus_type == "speed_down":
        for ball in balls:
            ball.speed_down()
    return lives


def _update_bonuses(
    bonuses: list[Bonus],
    paddle: Paddle,
    balls: list[Ball],
    lives: int,
    particles: list[Particle],
) -> int:
    """ Updates bonuses position, handles Paddle catch logic, returns number of lives. """
    for bonus in bonuses[:]:
        bonus.update()
        if bonus.rect.colliderect(paddle.rect):
            bonuses.remove(bonus)
            audio.play_sound(audio.bonus_sound)
            spawn_burst(particles, bonus.rect.center, bonus.color, count=6)
            lives = _apply_bonus(bonus.type, paddle, balls, lives)
        elif bonus.rect.top > cfg.HEIGHT:
            bonuses.remove(bonus)
    return lives


def _update_lasers(
    lasers: list[LaserBullet],
    bricks: list[Brick],
    bonuses: list[Bonus],
    particles: list[Particle],
) -> int:
    """ Handles laser's shots. """
    scored = 0
    for laser in lasers[:]:
        laser.update()
        hit_brick = False
        for brick in bricks[:]:
            if brick.hp == -1 or not laser.rect.colliderect(brick.rect):
                continue
            bonus_type = brick.hit()
            audio.play_sound(audio.hit_sound)
            if brick.hp <= 0:
                bricks.remove(brick)
                scored += 10
                spawn_burst(particles, brick.rect.center, brick.color)
                if bonus_type:
                    bonuses.append(Bonus(brick.rect.center, bonus_type))
            hit_brick = True
            break
        if hit_brick or laser.rect.bottom < 0:
            lasers.remove(laser)
    return scored


def _level_cleared(bricks: list[Brick]) -> bool:
    """ Checks if the level is completed (e.g. there are only indestructable bricks)."""
    return not any(brick.hp != -1 for brick in bricks)


def _draw_frame(
    screen: pygame.Surface,
    font: pygame.font.Font,
    paddle: Paddle,
    balls: list[Ball],
    bricks: list[Brick],
    bonuses: list[Bonus],
    lasers: list[LaserBullet],
    particles: list[Particle],
    score: int,
    lives: int,
) -> None:
    screen.fill(cfg.BLACK)
    paddle.draw(screen)
    for ball in balls:
        ball.draw(screen)
    for brick in bricks:
        brick.draw(screen)
    for bonus in bonuses:
        bonus.draw(screen)
    for laser in lasers:
        laser.draw(screen)
    draw_particles(screen, particles)

    hud = font.render(f"Points: {score}   Lives: {lives}", True, cfg.WHITE)
    screen.blit(hud, (10, 10))


def run(screen: pygame.Surface, clock: pygame.time.Clock, level: int) -> GameState:
    font = pygame.font.Font(None, 36)

    bricks, _rows, _cols = load_level(level)
    paddle = Paddle()
    balls = [_new_ball(paddle)]
    bonuses: list[Bonus] = []
    lasers: list[LaserBullet] = []
    particles: list[Particle] = []
    lives = 3
    score = 0
    last_shot = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameState.QUIT

        keys = pygame.key.get_pressed()
        paddle.move(keys)

        now = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and paddle.laser and now - last_shot > LASER_COOLDOWN:
            lasers.append(LaserBullet(paddle.rect.centerx, paddle.rect.top))
            last_shot = now

        score += _update_balls(balls, paddle, bricks, bonuses, particles)

        if not balls:
            lives -= 1
            if lives <= 0:
                return GameState.GAMEOVER
            balls.append(_new_ball(paddle))

        lives = _update_bonuses(bonuses, paddle, balls, lives, particles)
        score += _update_lasers(lasers, bricks, bonuses, particles)
        update_particles(particles)

        if _level_cleared(bricks):
            return GameState.WIN

        _draw_frame(screen, font, paddle, balls, bricks, bonuses, lasers, particles, score, lives)
        pygame.display.flip()
        clock.tick(cfg.FPS)
