"""Popup screen rendering for options and the introductory conversation."""

from __future__ import annotations

import pygame

INK = (137, 87, 67)
DARK = (91, 57, 48)
PAPER = (255, 250, 242)
HOVER = (255, 244, 213)
ACCENT = (222, 97, 24)
SHADOW = (153, 124, 113)


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
    """A bottom-anchored visual novel textbox, leaving the scene unobscured."""
    title = app.dialogue.current[0]
    lines = app.dialogue.visible_lines
    box = pygame.Rect(18, 78, 156, 27)
    pygame.draw.rect(app.canvas, SHADOW, box.move(1, 1))
    pygame.draw.rect(app.canvas, DARK, box)
    pygame.draw.rect(app.canvas, PAPER, box.inflate(-2, -2))
    pygame.draw.line(app.canvas, (255, 255, 255), (20, 80), (171, 80))
    nameplate = pygame.Rect(22, 69, 72, 10)
    pygame.draw.rect(app.canvas, DARK, nameplate)
    pygame.draw.rect(app.canvas, HOVER, nameplate.inflate(-2, -2))
    app.text(title, (26, 74), anchor="midleft", small=True, larger=True)
    for y, line in zip((86, 94, 102), lines):
        app.text(line, (23, y), anchor="midleft", small=True, larger=True)
    # A small breathing advance marker replaces the modal's separate button.
    offset = int(app.elapsed * 2) % 2
    pygame.draw.polygon(app.canvas, ACCENT,
                        ((164, 101 + offset), (168, 101 + offset), (166, 103 + offset)))


def draw_no_save(app, pointer: tuple[float, float]) -> None:
    app.popup(pygame.Rect(32, 32, 128, 49))
    app.text("NO SAVED GAME", (96, 43), title=True)
    app.text("START A NEW GAME?", (96, 55))
    app.button(pygame.Rect(46, 63, 45, 12), "NEW", pointer)
    app.button(pygame.Rect(101, 63, 45, 12), "BACK", pointer)
