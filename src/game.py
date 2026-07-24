"""Core play session: one level from spawn to level-clear / game-over."""

import random

import pygame

from src import config, levels, ui
from src.sprites import Ball, LaserBolt, Paddle, Particle, PowerUp, Star

MAX_BALLS = 6


def _resolve_circle_vs_rect(ball: Ball, rect: pygame.Rect) -> bool:
    """Push `ball` out of `rect` along the shallowest axis and reflect its
    velocity. Returns True if a collision actually happened."""
    if not ball.rect.colliderect(rect):
        return False

    overlap_left = ball.rect.right - rect.left
    overlap_right = rect.right - ball.rect.left
    overlap_top = ball.rect.bottom - rect.top
    overlap_bottom = rect.bottom - ball.rect.top
    shallowest = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

    if shallowest == overlap_top and ball.vel.y > 0:
        ball.pos.y -= overlap_top
        ball.vel.y *= -1
    elif shallowest == overlap_bottom and ball.vel.y < 0:
        ball.pos.y += overlap_bottom
        ball.vel.y *= -1
    elif shallowest == overlap_left and ball.vel.x > 0:
        ball.pos.x -= overlap_left
        ball.vel.x *= -1
    elif shallowest == overlap_right and ball.vel.x < 0:
        ball.pos.x += overlap_right
        ball.vel.x *= -1
    else:
        return True

    ball.rect.center = (round(ball.pos.x), round(ball.pos.y))
    return True


class Game:
    """Runs a single level. `run()` blocks until the level is won, all
    lives are lost, or the player quits, returning (result, score)."""

    def __init__(self, screen, clock, sounds, level_number, score=0, lives=None):
        self.screen = screen
        self.clock = clock
        self.sounds = sounds
        self.level_number = level_number
        self.score = score
        self.lives = config.START_LIVES if lives is None else lives

        self.paddle = Paddle()
        self.bricks = pygame.sprite.Group(levels.load_level(level_number))
        self.balls = pygame.sprite.Group(self._spawn_ball())
        self.powerups = pygame.sprite.Group()
        self.bolts = pygame.sprite.Group()
        self.particles: list[Particle] = []
        self.stars = [Star() for _ in range(70)]

        self.background = ui.vertical_gradient((config.WIDTH, config.HEIGHT), config.BG_TOP, config.BG_BOTTOM)
        self.message = ""
        self.message_timer = 0
        self.paused = False

    def _spawn_ball(self):
        ball = Ball(self.paddle.rect.centerx, self.paddle.rect.top - config.BALL_RADIUS)
        ball.stuck = True
        ball.stuck_offset = 0
        return ball

    def _spawn_particles(self, rect, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(rect.centerx, rect.centery, color))
            if len(self.particles) > 300:
                self.particles.pop(0)

    def _show_message(self, text):
        self.message = text
        self.message_timer = 90

    # -- event / input handling -------------------------------------------------
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_p):
                    self.paused = not self.paused
                elif event.key == pygame.K_SPACE:
                    for ball in self.balls:
                        ball.launch()
                elif event.key == pygame.K_x and self.paddle.has_laser:
                    self.bolts.add(LaserBolt(self.paddle.rect.left + 12, self.paddle.rect.top))
                    self.bolts.add(LaserBolt(self.paddle.rect.right - 12, self.paddle.rect.top))
                    self.sounds.laser.play()
        return None

    # -- physics -------------------------------------------------------------
    def _update_balls(self):
        lost_balls = []
        for ball in list(self.balls):
            if ball.stuck:
                ball.follow_paddle(self.paddle)
                continue

            wall_bounce = ball.update()
            if wall_bounce:
                self.sounds.wall.play()

            hit_brick = pygame.sprite.spritecollideany(ball, self.bricks)
            if hit_brick and _resolve_circle_vs_rect(ball, hit_brick.rect):
                if hit_brick.indestructible:
                    self.sounds.wall.play()
                else:
                    gained, bonus = hit_brick.hit()
                    self.sounds.brick.play()
                    if gained:
                        self.score += gained
                        self._spawn_particles(hit_brick.rect, config.BRICK_PALETTE[hit_brick.max_hp])
                        hit_brick.kill()
                        if bonus:
                            self.powerups.add(PowerUp(hit_brick.rect.centerx, hit_brick.rect.centery, bonus))

            if ball.vel.y > 0 and ball.rect.colliderect(self.paddle.rect):
                if self.paddle.sticky:
                    ball.stuck = True
                    ball.stuck_offset = ball.rect.centerx - self.paddle.rect.centerx
                else:
                    ball.bounce_off_paddle(self.paddle)
                self.sounds.paddle.play()

            if ball.rect.top > config.HEIGHT:
                lost_balls.append(ball)

        for ball in lost_balls:
            ball.kill()

        if not self.balls:
            self._handle_ball_lost()

    def _handle_ball_lost(self):
        if self.paddle.shield_charges > 0:
            self.paddle.shield_charges -= 1
            self._show_message("SHIELD ABSORBED THE HIT")
            self.balls.add(self._spawn_ball())
            return

        self.lives -= 1
        self.sounds.lose_life.play()
        if self.lives <= 0:
            return
        self.paddle.reset()
        self.balls.add(self._spawn_ball())

    def _update_powerups(self):
        for power in list(self.powerups):
            power.update()
            if power.rect.top > config.HEIGHT:
                power.kill()
            elif power.rect.colliderect(self.paddle.rect):
                self._apply_powerup(power.kind)
                power.kill()

    def _apply_powerup(self, kind):
        self.sounds.powerup.play()
        self._show_message(config.POWERUPS[kind]["caption"])
        if kind in ("wide", "narrow", "sticky", "laser", "shield"):
            self.paddle.apply_powerup(kind)
        elif kind == "life":
            self.lives += 1
        elif kind in ("haste", "calm"):
            for ball in self.balls:
                ball.apply_powerup(kind)
        elif kind == "multi":
            self._split_balls()

    def _split_balls(self):
        originals = [b for b in self.balls if not b.stuck]
        if not originals:
            return
        for ball in originals:
            if len(self.balls) >= MAX_BALLS:
                break
            for angle in (-24, 24):
                if len(self.balls) >= MAX_BALLS:
                    break
                clone = Ball(ball.pos.x, ball.pos.y, ball.vel.rotate(angle))
                clone.stuck = False
                self.balls.add(clone)

    def _update_bolts(self):
        for bolt in list(self.bolts):
            bolt.update()
            if bolt.rect.bottom < 0:
                bolt.kill()
                continue
            hit_brick = pygame.sprite.spritecollideany(bolt, self.bricks)
            if hit_brick:
                gained = hit_brick.destroy_instantly()
                self.sounds.brick.play()
                bolt.kill()
                if gained:
                    self.score += gained
                    self._spawn_particles(hit_brick.rect, config.BRICK_PALETTE[hit_brick.max_hp])
                    hit_brick.kill()

    def _level_cleared(self):
        return not any(not b.indestructible for b in self.bricks)

    # -- drawing -------------------------------------------------------------
    def _draw_hud(self):
        panel_rect = pygame.Rect(0, 0, config.WIDTH, config.FIELD_TOP - 20)
        ui.draw_panel(self.screen, panel_rect, alpha=140, radius=0)

        ui.draw_text(self.screen, f"SCORE {self.score:05d}", 26, config.WHITE, (110, 30), bold=True)
        ui.draw_text(self.screen, f"LEVEL {self.level_number}", 26, config.NEON_YELLOW, (config.WIDTH // 2, 30), bold=True)

        for i in range(self.lives):
            x = config.WIDTH - 30 - i * 26
            pygame.draw.rect(self.screen, config.PADDLE_COLOR, (x, 20, 18, 8), border_radius=3)

        if self.paddle.shield_charges:
            ui.draw_text(self.screen, f"SHIELD x{self.paddle.shield_charges}", 18, config.WHITE, (config.WIDTH // 2, 60))

        if self.message_timer > 0:
            self.message_timer -= 1
            ui.draw_text(self.screen, self.message, 24, config.NEON_YELLOW, (config.WIDTH // 2, config.HEIGHT - 22), bold=True)

    def _draw_ball_trail(self, ball):
        for i, pos in enumerate(ball.trail):
            alpha = int(160 * (i + 1) / max(1, len(ball.trail)))
            radius = max(1, ball.radius - 2)
            trail_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (*config.BALL_COLOR, alpha), (radius, radius), radius)
            self.screen.blit(trail_surf, (pos[0] - radius, pos[1] - radius))

    def _draw(self):
        self.screen.blit(self.background, (0, 0))
        for star in self.stars:
            star.update()
            star.draw(self.screen)

        self.bricks.draw(self.screen)
        for ball in self.balls:
            self._draw_ball_trail(ball)
        self.balls.draw(self.screen)
        self.screen.blit(self.paddle.image, self.paddle.rect)
        self.powerups.draw(self.screen)
        self.bolts.draw(self.screen)

        for particle in self.particles:
            particle.draw(self.screen)

        self._draw_hud()

        if self.paused:
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            ui.draw_text(self.screen, "PAUSED", 60, config.WHITE, (config.WIDTH // 2, config.HEIGHT // 2), bold=True)
            ui.draw_text(self.screen, "Press ESC or P to resume", 24, config.DIM, (config.WIDTH // 2, config.HEIGHT // 2 + 50))

    # -- main loop -------------------------------------------------------------
    def run(self):
        while True:
            outcome = self._handle_events()
            if outcome == "quit":
                return "quit", self.score

            if not self.paused:
                keys = pygame.key.get_pressed()
                self.paddle.handle_input(keys)
                self.paddle.update()

                self._update_balls()
                if self.lives <= 0:
                    return "game_over", self.score

                self._update_powerups()
                self._update_bolts()

                self.particles = [p for p in self.particles if p.update()]

                if self._level_cleared():
                    return "level_clear", self.score

            self._draw()
            pygame.display.flip()
            self.clock.tick(config.FPS)
