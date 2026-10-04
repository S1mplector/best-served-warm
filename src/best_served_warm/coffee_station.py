"""Clickable cup choices and pixel-style cups placed on the cafe counter."""

from __future__ import annotations

import pygame


STATION_SIZE = (1672, 940)
COUNTER = pygame.Rect(14, 570, 1644, 190)

# Bounds follow the visible cup silhouettes and matching S/M/L plaques in the
# supplied station artwork. Each choice is a full cup-plus-label target.
CHOICES = (
    ("takeaway", "S", pygame.Rect(274, 379, 106, 180), (76, 107)),
    ("takeaway", "M", pygame.Rect(397, 340, 119, 219), (90, 137)),
    ("takeaway", "L", pygame.Rect(528, 297, 130, 262), (102, 162)),
    ("cold", "S", pygame.Rect(744, 374, 97, 185), (68, 109)),
    ("cold", "M", pygame.Rect(864, 341, 124, 218), (84, 141)),
    ("cold", "L", pygame.Rect(996, 306, 132, 253), (98, 165)),
    ("mug", "S", pygame.Rect(1200, 404, 114, 155), (75, 100)),
    ("mug", "M", pygame.Rect(1315, 372, 140, 187), (93, 127)),
    ("mug", "L", pygame.Rect(1446, 342, 165, 217), (111, 152)),
)

OUTLINE = (54, 39, 39, 255)
PAPER = (241, 215, 180, 255)
PAPER_SHADE = (191, 126, 83, 255)
CREAM = (251, 229, 194, 255)
LID = (55, 45, 47, 255)
LID_HIGHLIGHT = (132, 119, 111, 255)
GLASS = (221, 217, 202, 155)
GLASS_LIGHT = (255, 242, 213, 205)


class CoffeeStation:
    def __init__(self) -> None:
        self.overlay = pygame.Surface(STATION_SIZE, pygame.SRCALPHA)
        self.placed: list[dict] = []
        self.held: dict | None = None
        self.pointer = (0.0, 0.0)

    def move_pointer(self, point: tuple[float, float]) -> None:
        self.pointer = point

    def _item_rect(self, item: dict, *, at_pointer: bool = False) -> pygame.Rect:
        width, height = item["dimensions"]
        x, bottom = self.pointer if at_pointer else (item["x"], item["bottom"])
        return pygame.Rect(round(x - width / 2), round(bottom - height), width, height)

    def click(self, point: tuple[float, float]) -> str | None:
        """Pick a rack cup or place the held cup with a second counter click."""
        self.pointer = point
        if self.held is not None:
            if not COUNTER.collidepoint(point):
                return None
            width, height = self.held["dimensions"]
            x = min(max(point[0], COUNTER.left + width / 2), COUNTER.right - width / 2)
            bottom = min(max(point[1], COUNTER.top + height + 3), COUNTER.bottom - 3)
            item = {**self.held, "x": x, "bottom": bottom}
            self.placed.append(item)
            self.held = None
            return "placed"

        for index in range(len(self.placed) - 1, -1, -1):
            item = self.placed[index]
            if self._item_rect(item).collidepoint(point):
                self.held = self.placed.pop(index)
                return "picked"

        for style, size, bounds, dimensions in CHOICES:
            if bounds.collidepoint(point):
                self.held = {"style": style, "size": size, "dimensions": dimensions}
                return "picked"
        return None

    def draw(self, pointer: tuple[float, float]) -> pygame.Surface:
        self.pointer = pointer
        self.overlay.fill((0, 0, 0, 0))
        if self.held is None:
            for _style, _size, bounds, _dimensions in CHOICES:
                if bounds.collidepoint(pointer):
                    pygame.draw.rect(self.overlay, (255, 195, 104, 42), bounds)
                    pygame.draw.rect(self.overlay, (255, 223, 170, 220), bounds, 4)
                    break
        for item in self.placed:
            self._draw_cup(item, item["x"], item["bottom"])
        if self.held is not None:
            self._draw_cup(self.held, pointer[0], pointer[1])
        return self.overlay

    def _draw_cup(self, item: dict, center_x: float, bottom: float) -> None:
        surface = self.overlay
        width, height = item["dimensions"]
        left = round(center_x - width / 2)
        top = round(bottom - height)
        if item["style"] == "takeaway":
            self._draw_takeaway(surface, left, top, width, height)
        elif item["style"] == "cold":
            self._draw_cold(surface, left, top, width, height)
        else:
            self._draw_mug(surface, left, top, width, height)

    @staticmethod
    def _draw_takeaway(surface: pygame.Surface, x: int, y: int, w: int, h: int) -> None:
        lid_h = max(12, h // 6)
        body_top = y + lid_h - 2
        body_bottom = y + h - 3
        top_half, base_half = round(w * 0.43), round(w * 0.32)
        outer = ((x + w // 2 - top_half, body_top), (x + w // 2 + top_half, body_top),
                 (x + w // 2 + base_half, body_bottom), (x + w // 2 - base_half, body_bottom))
        pygame.draw.polygon(surface, OUTLINE, outer)
        inner = ((outer[0][0] + 3, body_top + 3), (outer[1][0] - 3, body_top + 3),
                 (outer[2][0] - 3, body_bottom - 3), (outer[3][0] + 3, body_bottom - 3))
        pygame.draw.polygon(surface, PAPER, inner)
        sleeve_top = body_top + round((body_bottom - body_top) * 0.34)
        sleeve_bottom = body_top + round((body_bottom - body_top) * 0.74)
        sleeve = ((x + w // 2 - round(w * 0.38), sleeve_top),
                  (x + w // 2 + round(w * 0.38), sleeve_top),
                  (x + w // 2 + round(w * 0.35), sleeve_bottom),
                  (x + w // 2 - round(w * 0.35), sleeve_bottom))
        pygame.draw.polygon(surface, PAPER_SHADE, sleeve)
        pygame.draw.line(surface, (221, 165, 115, 255), sleeve[0], sleeve[1], 2)
        pygame.draw.line(surface, CREAM, (x + w // 2 - 2, body_top + 8),
                         (x + w // 2 - 2, body_bottom - 8), 2)
        lid = pygame.Rect(x + round(w * 0.12), y + 2, round(w * 0.76), lid_h)
        pygame.draw.rect(surface, OUTLINE, lid)
        pygame.draw.rect(surface, LID, lid.inflate(-4, -4))
        pygame.draw.rect(surface, LID_HIGHLIGHT, (lid.left + 5, lid.top + 4, lid.width - 10, 3))
        pygame.draw.rect(surface, OUTLINE, (x + round(w * 0.08), y + lid_h - 1,
                                            round(w * 0.84), 5))
        pygame.draw.rect(surface, LID_HIGHLIGHT, (x + round(w * 0.18), y + lid_h,
                                                   round(w * 0.64), 2))

    @staticmethod
    def _draw_cold(surface: pygame.Surface, x: int, y: int, w: int, h: int) -> None:
        rim_h = max(9, h // 9)
        body_top, body_bottom = y + rim_h, y + h - 3
        top_half, base_half = round(w * 0.43), round(w * 0.30)
        outer = ((x + w // 2 - top_half, body_top), (x + w // 2 + top_half, body_top),
                 (x + w // 2 + base_half, body_bottom), (x + w // 2 - base_half, body_bottom))
        pygame.draw.polygon(surface, OUTLINE, outer)
        inner = ((outer[0][0] + 3, body_top + 3), (outer[1][0] - 3, body_top + 3),
                 (outer[2][0] - 3, body_bottom - 3), (outer[3][0] + 3, body_bottom - 3))
        pygame.draw.polygon(surface, GLASS, inner)
        pygame.draw.rect(surface, OUTLINE, (x + round(w * 0.05), y + 2, round(w * 0.90), rim_h))
        pygame.draw.rect(surface, GLASS_LIGHT, (x + round(w * 0.10), y + 5,
                                                round(w * 0.80), max(3, rim_h - 6)))
        pygame.draw.line(surface, GLASS_LIGHT, (x + round(w * 0.22), body_top + 9),
                         (x + round(w * 0.17), body_bottom - 8), 4)
        pygame.draw.line(surface, (157, 143, 130, 210), (x + round(w * 0.76), body_top + 12),
                         (x + round(w * 0.70), body_bottom - 7), 2)
        pygame.draw.line(surface, GLASS_LIGHT, (outer[3][0] + 4, body_bottom - 5),
                         (outer[2][0] - 4, body_bottom - 5), 3)

    @staticmethod
    def _draw_mug(surface: pygame.Surface, x: int, y: int, w: int, h: int) -> None:
        handle = pygame.Rect(x + round(w * 0.70), y + round(h * 0.28),
                             round(w * 0.30), round(h * 0.47))
        pygame.draw.ellipse(surface, OUTLINE, handle)
        pygame.draw.ellipse(surface, (0, 0, 0, 0), handle.inflate(-7, -7))
        body = pygame.Rect(x + round(w * 0.07), y + round(h * 0.17),
                           round(w * 0.70), round(h * 0.78))
        pygame.draw.rect(surface, OUTLINE, body)
        pygame.draw.rect(surface, PAPER, body.inflate(-4, -4))
        pygame.draw.rect(surface, CREAM, (body.left + 6, body.top + 7, 4, body.height - 17))
        pygame.draw.rect(surface, PAPER_SHADE,
                         (body.left + 5, body.bottom - 14, body.width - 10, 5))
        pygame.draw.rect(surface, OUTLINE, (body.left - 2, body.top - 3, body.width + 4, 7))
        pygame.draw.rect(surface, PAPER_SHADE, (body.left + 5, body.top, body.width - 10, 2))
