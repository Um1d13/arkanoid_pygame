"""Game entities.

Paddle, Ball, Brick, PowerUp and LaserBolt are real pygame.sprite.Sprite
subclasses managed through sprite Groups (collision + draw handled by
the group machinery). Particle and Star are cheap, short-lived visual
flourishes kept in plain lists instead, since they never need group
collision queries.
"""

import random

import pygame

from src import config


def _rounded_surface(size, color, radius=4):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(surf, color, surf.get_rect(), border_radius=radius)
    return surf


class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.base_width = config.PADDLE_W
        self.width = self.base_width
        self.height = config.PADDLE_H
        self.image = _rounded_surface((self.width, self.height), config.PADDLE_COLOR, radius=6)
        self.rect = self.image.get_rect()
        self.rect.midbottom = (config.WIDTH // 2, config.HEIGHT - config.PADDLE_Y_OFFSET)
        self.speed = config.PADDLE_SPEED
        self.effects = {"wide": 0, "narrow": 0, "sticky": 0, "laser": 0}
        self.shield_charges = 0

    def _rebuild(self, width):
        center = self.rect.centerx
        self.width = width
        self.image = _rounded_surface((self.width, self.height), config.PADDLE_COLOR, radius=6)
        self.rect = self.image.get_rect()
        self.rect.centerx = center
        self.rect.bottom = config.HEIGHT - config.PADDLE_Y_OFFSET
        self._clamp()

    def _clamp(self):
        if self.rect.left < config.FIELD_LEFT:
            self.rect.left = config.FIELD_LEFT
        if self.rect.right > config.FIELD_RIGHT:
            self.rect.right = config.FIELD_RIGHT

    def reset(self):
        self.effects = {"wide": 0, "narrow": 0, "sticky": 0, "laser": 0}
        self.shield_charges = 0
        self._rebuild(self.base_width)
        self.rect.centerx = config.WIDTH // 2

    @property
    def sticky(self):
        return self.effects["sticky"] > 0

    @property
    def has_laser(self):
        return self.effects["laser"] > 0

    def apply_powerup(self, kind):
        if kind == "wide":
            self.effects["narrow"] = 0
            self._rebuild(config.PADDLE_WIDE)
            self.effects["wide"] = config.POWERUP_DURATION
        elif kind == "narrow":
            self.effects["wide"] = 0
            self._rebuild(config.PADDLE_NARROW)
            self.effects["narrow"] = config.POWERUP_DURATION
        elif kind == "sticky":
            self.effects["sticky"] = config.POWERUP_DURATION
        elif kind == "laser":
            self.effects["laser"] = config.POWERUP_DURATION
        elif kind == "shield":
            self.shield_charges += 1

    def handle_input(self, keys):
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        self.rect.x += dx
        self._clamp()

    def update(self):
        for name in ("wide", "narrow", "sticky", "laser"):
            if self.effects[name] > 0:
                self.effects[name] -= 1
                if self.effects[name] == 0 and name in ("wide", "narrow"):
                    self._rebuild(self.base_width)


class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, vel=None):
        super().__init__()
        self.radius = config.BALL_RADIUS
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, config.BALL_COLOR, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        if vel is None:
            angle = random.uniform(-35, 35)
            vel = pygame.math.Vector2(0, -config.BALL_SPEED).rotate(angle)
        self.vel = vel
        self.stuck = True
        self.stuck_offset = 0
        self.trail = []
        self.haste_timer = 0
        self.calm_timer = 0

    def launch(self):
        if self.stuck:
            self.stuck = False
            angle = random.uniform(-20, 20)
            self.vel = pygame.math.Vector2(0, -config.BALL_SPEED).rotate(angle)

    def apply_powerup(self, kind):
        if kind == "haste" and self.calm_timer == 0:
            self.vel *= config.BALL_HASTE_MULT
            self.haste_timer = config.POWERUP_DURATION
        elif kind == "calm" and self.haste_timer == 0:
            self.vel *= config.BALL_CALM_MULT
            self.calm_timer = config.POWERUP_DURATION

    def follow_paddle(self, paddle):
        self.pos.x = paddle.rect.centerx + self.stuck_offset
        self.pos.y = paddle.rect.top - self.radius
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def update(self):
        if self.haste_timer > 0:
            self.haste_timer -= 1
            if self.haste_timer == 0:
                self.vel /= config.BALL_HASTE_MULT
        if self.calm_timer > 0:
            self.calm_timer -= 1
            if self.calm_timer == 0:
                self.vel /= config.BALL_CALM_MULT

        if self.stuck:
            return

        self.trail.append(tuple(self.pos))
        if len(self.trail) > 8:
            self.trail.pop(0)

        self.pos += self.vel
        bounced_wall = False
        if self.pos.x - self.radius < config.FIELD_LEFT:
            self.pos.x = config.FIELD_LEFT + self.radius
            self.vel.x *= -1
            bounced_wall = True
        elif self.pos.x + self.radius > config.FIELD_RIGHT:
            self.pos.x = config.FIELD_RIGHT - self.radius
            self.vel.x *= -1
            bounced_wall = True
        if self.pos.y - self.radius < config.FIELD_TOP - config.BRICK_H:
            self.pos.y = config.FIELD_TOP - config.BRICK_H + self.radius
            self.vel.y *= -1
            bounced_wall = True

        self.rect.center = (round(self.pos.x), round(self.pos.y))
        return bounced_wall

    def bounce_off_paddle(self, paddle):
        offset = (self.pos.x - paddle.rect.centerx) / (paddle.rect.width / 2)
        offset = max(-1.0, min(1.0, offset))
        angle = offset * config.BALL_MAX_BOUNCE_ANGLE
        speed = self.vel.length()
        self.vel = pygame.math.Vector2(0, -speed).rotate(angle)
        self.pos.y = paddle.rect.top - self.radius
        self.rect.center = (round(self.pos.x), round(self.pos.y))


class Brick(pygame.sprite.Sprite):
    def __init__(self, col, row, hp):
        super().__init__()
        self.hp = hp
        self.max_hp = hp
        self.rect = pygame.Rect(
            config.FIELD_LEFT + col * config.BRICK_W,
            config.FIELD_TOP + row * config.BRICK_H,
            config.BRICK_W - 2,
            config.BRICK_H - 2,
        )
        self._rebuild()

    def _rebuild(self):
        color = config.STEEL_COLOR if self.hp == -1 else config.BRICK_PALETTE[self.hp]
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, self.image.get_rect(), border_radius=3)
        light = tuple(min(255, c + 55) for c in color)
        dark = tuple(max(0, c - 55) for c in color)
        pygame.draw.line(self.image, light, (2, 2), (self.rect.width - 3, 2), 2)
        pygame.draw.line(self.image, dark, (2, self.rect.height - 3), (self.rect.width - 3, self.rect.height - 3), 2)

    @property
    def indestructible(self):
        return self.hp == -1

    def hit(self):
        """Apply one ball hit. Returns (score_gained, powerup_kind_or_None)."""
        if self.indestructible:
            return 0, None
        self.hp -= 1
        if self.hp <= 0:
            gained = config.BRICK_SCORE[self.max_hp]
            bonus = random.choice(list(config.POWERUPS)) if random.random() < config.POWERUP_DROP_CHANCE else None
            return gained, bonus
        self._rebuild()
        return 0, None

    def destroy_instantly(self):
        """Used by laser bolts. Returns score gained (0 if steel)."""
        if self.indestructible:
            return 0
        return config.BRICK_SCORE[self.max_hp]


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, kind):
        super().__init__()
        self.kind = kind
        info = config.POWERUPS[kind]
        w, h = config.POWERUP_SIZE
        self.image = _rounded_surface((w, h), info["color"], radius=4)
        font = pygame.font.Font(None, 18)
        label = font.render(info["label"], True, config.PANEL)
        self.image.blit(label, label.get_rect(center=(w // 2, h // 2)))
        self.rect = self.image.get_rect(center=(x, y))
        self.fall_speed = config.POWERUP_FALL_SPEED

    def update(self):
        self.rect.y += self.fall_speed


class LaserBolt(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((3, 14), pygame.SRCALPHA)
        pygame.draw.rect(self.image, config.NEON_PINK, self.image.get_rect(), border_radius=2)
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = -11

    def update(self):
        self.rect.y += self.speed


class Particle:
    """One-shot debris flecks spawned when a brick is destroyed."""

    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "size")

    def __init__(self, x, y, color):
        self.x, self.y = x, y
        angle = random.uniform(0, 360)
        speed = random.uniform(1.2, 3.6)
        vec = pygame.math.Vector2(speed, 0).rotate(angle)
        self.vx, self.vy = vec.x, vec.y
        self.max_life = random.randint(16, 30)
        self.life = self.max_life
        self.color = color
        self.size = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.12
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        alpha = max(0, int(255 * (self.life / self.max_life)))
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill((*self.color, alpha))
        surface.blit(s, (self.x, self.y))


class Star:
    """Slow-drifting background twinkle, purely decorative."""

    __slots__ = ("x", "y", "radius", "speed", "phase")

    def __init__(self):
        self.x = random.uniform(0, config.WIDTH)
        self.y = random.uniform(0, config.HEIGHT)
        self.radius = random.uniform(0.6, 1.8)
        self.speed = random.uniform(0.1, 0.5)
        self.phase = random.uniform(0, 6.28)

    def update(self):
        self.y += self.speed
        if self.y > config.HEIGHT:
            self.y = 0
            self.x = random.uniform(0, config.WIDTH)
        self.phase += 0.05

    def draw(self, surface):
        import math
        brightness = 120 + int(80 * (0.5 + 0.5 * math.sin(self.phase)))
        color = (brightness, brightness, brightness + 20)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
