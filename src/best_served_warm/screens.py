"""Popup screen rendering for options and the introductory conversation."""

from __future__ import annotations

import math

import pygame

INK = (137, 87, 67)
DARK = (91, 57, 48)
PAPER = (255, 250, 242)
HOVER = (255, 244, 213)
ACCENT = (222, 97, 24)
SHADOW = (153, 124, 113)
DIALOGUE_OUTLINE = (91, 57, 43)
DIALOGUE_RIM = (165, 108, 73)
DIALOGUE_FACE = (234, 214, 180)
DIALOGUE_LABEL = (214, 181, 137)
DIALOGUE_INK = (76, 47, 38)


def _stepped_rect(rect: pygame.Rect, cut: int = 3) -> list[tuple[int, int]]:
    """Pixel-cut corners for a small hand-built panel silhouette."""
    left, top, right, bottom = rect.left, rect.top, rect.right - 1, rect.bottom - 1
    return [
        (left + cut, top), (right - cut, top),
        (right - cut, top + 1), (right, top + 1),
        (right, bottom - 1), (right - cut, bottom - 1),
        (right - cut, bottom), (left + cut, bottom),
        (left + cut, bottom - 1), (left, bottom - 1),
        (left, top + 1), (left + cut, top + 1),
    ]


def _pixel_panel(surface: pygame.Surface, rect: pygame.Rect,
                 face: tuple[int, int, int]) -> None:
    """Layer a warm stepped frame, thin caramel rim, and soft offset shadow."""
    shadow = tuple(rect.move(2, 2))
    pygame.draw.polygon(surface, (73, 47, 38, 150), _stepped_rect(pygame.Rect(shadow)))
    pygame.draw.polygon(surface, DIALOGUE_OUTLINE, _stepped_rect(rect))
    inset = rect.inflate(-2, -2)
    pygame.draw.polygon(surface, DIALOGUE_RIM, _stepped_rect(inset, 1))
    inner = rect.inflate(-3, -3)
    pygame.draw.polygon(surface, face, _stepped_rect(inner, 1))
    # Broken highlight marks keep the rim crisp without a smooth, continuous edge.
    pygame.draw.rect(surface, (247, 226, 188), (rect.left + 5, rect.top + 2, 18, 1))
    pygame.draw.rect(surface, (247, 226, 188), (rect.right - 12, rect.top + 2, 5, 1))


def draw_options(app, pointer: tuple[float, float]) -> None:
    app.popup(pygame.Rect(27, 16, 138, 91))
    app.text("OPTIONS", (96, 26), title=True)
    pygame.draw.line(app.canvas, INK, (38, 34), (154, 34))
    app.text(f"MUSIC  {round(app.options['volume'] * 100)}%", (96, 42))
    track = pygame.Rect(39, 50, 114, 4)
    pygame.draw.rect(app.canvas, INK, track)
    pygame.draw.rect(app.canvas, ACCENT, (track.left + 1, track.top + 1,
                     round((track.width - 2) * app.options["volume"]), 2))
    knob_x = track.left + round((track.width - 1) * app.options["volume"])
    pygame.draw.rect(app.canvas, PAPER, (knob_x - 2, 48, 5, 8))
    pygame.draw.rect(app.canvas, INK, (knob_x - 2, 48, 5, 8), 1)
    app.text("FULLSCREEN", (72, 67))
    app.button(pygame.Rect(120, 60, 34, 13), "ON" if app.options["fullscreen"] else "OFF", pointer)
    app.button(pygame.Rect(68, 79, 56, 13), "SAVE & BACK", pointer)
    volume = app.options['typing_volume']
    label = 'OFF' if volume == 0 else f'{round(volume * 100)}%'
    app.button(pygame.Rect(38, 94, 116, 10), f'TYPING SOUND: {label}', pointer)


def draw_dialogue(app, pointer: tuple[float, float]) -> None:
    """Draw a compact visual-novel textbox over the live bakery scene."""
    title = app.dialogue.current[0]
    lines = app.dialogue.visible_lines
    box = pygame.Rect(18, 78, 156, 27)
    _pixel_panel(app.canvas, box, DIALOGUE_FACE)
    nameplate = pygame.Rect(22, 69, 72, 10)
    _pixel_panel(app.canvas, nameplate, DIALOGUE_LABEL)
    app.text(title, (26, 74), anchor="midleft", small=True, larger=True, color=DIALOGUE_INK)
    for y, line in zip((84, 92, 100), lines):
        app.text(line, (23, y), anchor="midleft", small=True, larger=True, color=DIALOGUE_INK)
    # A small breathing advance marker replaces the modal's separate button.
    offset = int(app.elapsed * 2) % 2
    pygame.draw.polygon(app.canvas, ACCENT,
                        ((164, 101 + offset), (168, 101 + offset), (166, 103 + offset)))


def draw_loading(app) -> None:
    """Minimal black loading screen with the sleeping cat and pixel spinner."""
    app.canvas.fill((0, 0, 0))
    cat_width = 32
    cat_height = max(1, round(app.loading_cat.get_height() * cat_width / app.loading_cat.get_width()))
    cat = pygame.transform.scale(app.loading_cat, (cat_width, cat_height))
    app.canvas.blit(cat, cat.get_rect(center=(96, 44)))

    center = (96, 73)
    radius = 8
    active = round(app.loading_elapsed * 9) % 8
    for index in range(8):
        angle = index * 3.14159265 / 4
        x = round(center[0] + radius * math.cos(angle))
        y = round(center[1] + radius * math.sin(angle))
        distance = (index - active) % 8
        brightness = max(72, 240 - distance * 24)
        pygame.draw.rect(app.canvas, (brightness, brightness, brightness), (x, y, 2, 2))


def draw_no_save(app, pointer: tuple[float, float]) -> None:
    app.popup(pygame.Rect(32, 32, 128, 49))
    app.text("NO SAVED GAME", (96, 43), title=True)
    app.text("START A NEW GAME?", (96, 55))
    app.button(pygame.Rect(46, 63, 45, 12), "NEW", pointer)
    app.button(pygame.Rect(101, 63, 45, 12), "BACK", pointer)
