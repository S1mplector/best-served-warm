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
    app.popup(pygame.Rect(27, 16, 138, 82))
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


def draw_dialogue(app, pointer: tuple[float, float]) -> None:
    title, *lines = app.dialogue.current
    app.popup(pygame.Rect(17, 22, 158, 64))
    app.text(title, (96, 33), title=True)
    pygame.draw.line(app.canvas, INK, (28, 41), (164, 41))
    for y, line in zip((51, 60, 69, 78), lines):
        app.text(line, (96, y))
    label = "CONTINUE" if not app.dialogue.is_last_page else "BACK TO MENU"
    app.button(pygame.Rect(63, 89, 66, 13), label, pointer)


def draw_no_save(app, pointer: tuple[float, float]) -> None:
    app.popup(pygame.Rect(32, 32, 128, 49))
    app.text("NO SAVED GAME", (96, 43), title=True)
    app.text("START A NEW GAME?", (96, 55))
    app.button(pygame.Rect(46, 63, 45, 12), "NEW", pointer)
    app.button(pygame.Rect(101, 63, 45, 12), "BACK", pointer)
