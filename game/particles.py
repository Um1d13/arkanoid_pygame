"""game/particles.py – Pixelated particles for the VFX
"""

import math
import random

import pygame

import settings as cfg

Color = tuple[int, int, int]


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "color", "size", "life", "max_life")

    def __init__(self, x: float, y: float, color: Color) -> None:
        angle = random.uniform(0, math.tau)
        speed = random.uniform(*cfg.PARTICLE_SPEED)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.size = random.randint(2, 4)
        self.max_life = random.randint(*cfg.PARTICLE_LIFETIME)
        self.life = self.max_life

    @property
    def alive(self) -> bool:
        return self.life > 0

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.vy += cfg.PARTICLE_GRAVITY
        self.life -= 1

    def draw(self, screen: pygame.Surface) -> None:
        fade = self.life / self.max_life
        size = max(1, round(self.size * fade))
        pygame.draw.rect(screen, self.color, (int(self.x), int(self.y), size, size))


def spawn_burst(
    particles: list[Particle],
    center: tuple[int, int],
    color: Color,
    count: int = cfg.PARTICLE_COUNT,
) -> None:
    """ Adds count to the particles list. """
    x, y = center
    particles.extend(Particle(x, y, color) for _ in range(count))
    overflow = len(particles) - cfg.MAX_PARTICLES
    if overflow > 0:
        del particles[:overflow] 


def update_particles(particles: list[Particle]) -> None:
    """ Updates patricles and removes dead ones. """
    for particle in particles[:]:
        particle.update()
        if not particle.alive:
            particles.remove(particle)


def draw_particles(screen: pygame.Surface, particles: list[Particle]) -> None:
    for particle in particles:
        particle.draw(screen)
