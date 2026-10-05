"""Drawing helpers for temporary station views; no gameplay rules live here."""
from __future__ import annotations

import pygame
from .paths import asset_path

SIZE = (640, 360)
INK = (78, 54, 43)
PAPER = (255, 246, 225)
CREAM = (239, 219, 183)
WOOD = (173, 119, 79)
SAGE = (86, 116, 91)
PALE = (184, 202, 166)
RUST = (173, 83, 48)
MUTED = (139, 113, 88)
STAGES = ('Cup', 'Beans', 'Grind & tamp', 'Extract', 'Finish')


class Workbench:
    def __init__(self, app):
        self.app = app
        self.surface = pygame.Surface(SIZE)
        self.font = pygame.font.Font(str(asset_path('fonts', 'm5x7.ttf')), 16)
        self.title_font = pygame.font.Font(str(asset_path('fonts', 'm5x7.ttf')), 32)
        self.sprites = {}
        for path in asset_path('barista').glob('*.png'):
            self.sprites[path.stem] = pygame.image.load(str(path)).convert_alpha()
        self.controls = []
        self.holding = None
        self.category = 'milk'
        self.hovered = None
        self.pour = 0.0
        self.time = 0.0

    def pointer(self, pos):
        w, h = self.app.window.get_size()
        return pos[0] * SIZE[0] / w, pos[1] * SIZE[1] / h

    def text(self, text, x, y, color=INK, *, title=False, center=False):
        font = self.title_font if title else self.font
        glyphs = font.render(str(text), False, color)
        w, h = self.app.window.get_size()
        scale = max(1, round(min(w / SIZE[0], h / SIZE[1])))
        if scale > 1:
            glyphs = pygame.transform.scale(glyphs, (glyphs.get_width()*scale, glyphs.get_height()*scale))
        rect = glyphs.get_rect()
        if center:
            rect.center = (round(x*w/SIZE[0]), round(y*h/SIZE[1]))
        else:
            rect.midleft = (round(x*w/SIZE[0]), round(y*h/SIZE[1]))
        self.app.text_layer.blit(glyphs, rect)

    def panel(self, rect, color=PAPER):
        r = pygame.Rect(rect)
        pygame.draw.rect(self.surface, MUTED, r.move(2, 3))
        pygame.draw.rect(self.surface, INK, r)
        pygame.draw.rect(self.surface, color, r.inflate(-2, -2))
        pygame.draw.line(self.surface, (255, 252, 240), (r.left+2,r.top+2),(r.right-3,r.top+2))

    def button(self, action, rect, label, pointer, *, active=False, enabled=True):
        r = pygame.Rect(rect)
        hover = enabled and r.collidepoint(pointer)
        fill = PALE if active else (255, 235, 191) if hover else PAPER if enabled else CREAM
        self.panel(r, fill)
        self.text(label, *r.center, color=INK if enabled else MUTED, center=True)
        if enabled:
            self.controls.append((action, r))

    def icon(self, name, center, scale=1):
        sprite = self.sprites[name]
        image = pygame.transform.scale(sprite, (sprite.get_width()*scale, sprite.get_height()*scale))
        self.surface.blit(image, image.get_rect(center=center))

    def target(self, point):
        return next((action for action,r in reversed(self.controls) if r.collidepoint(point)), None)
