"""Reusable drawing helpers: gradients, panels and mouse-driven buttons."""

import pygame

from src import config

_FONT_CACHE = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _FONT_CACHE:
        f = pygame.font.Font(None, size)
        f.set_bold(bold)
        _FONT_CACHE[key] = f
    return _FONT_CACHE[key]


def draw_text(surface, text, size, color, center, bold=False):
    surf = font(size, bold).render(text, True, color)
    rect = surf.get_rect(center=center)
    surface.blit(surf, rect)
    return rect


def vertical_gradient(size, top_color, bottom_color):
    surf = pygame.Surface(size)
    h = size[1]
    for y in range(h):
        t = y / max(1, h - 1)
        color = tuple(int(top_color[i] + (bottom_color[i] - top_color[i]) * t) for i in range(3))
        pygame.draw.line(surf, color, (0, y), (size[0], y))
    return surf


def draw_panel(surface, rect, alpha=180, radius=10):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, (*config.PANEL, alpha), panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, config.NEON_CYAN, panel.get_rect(), width=2, border_radius=radius)
    surface.blit(panel, rect.topleft)


class Button:
    def __init__(self, rect, label, size=32):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.size = size
        self.hovered = False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self, surface):
        bg = config.NEON_CYAN if self.hovered else config.PANEL
        text_color = config.PANEL if self.hovered else config.WHITE
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, config.NEON_CYAN, self.rect, width=2, border_radius=8)
        draw_text(surface, self.label, self.size, text_color, self.rect.center, bold=True)
