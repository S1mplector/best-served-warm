"""Popup screen rendering for options and the introductory conversation."""

from __future__ import annotations

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
    portrait = {"LENA": app.lena_portrait, "SAM": app.sam_portrait,
                "MRS HEATHER": app.heather_portrait}.get(title)
    if portrait:
        width, height = app.text_layer.get_size()
        # Keep the source pixels intact and enlarge them at a uniform integer
        # scale. Draw onto the scene first; the dialogue panels then cover the
        # sprite's lower edge so the character feels planted behind the box.
        pixel_scale = max(1, round(height / 216))
        box_top = round(76 * height / 108)
        sprite_bottom = box_top + round(4 * height / 108)
        # Use one shared scale and anchor for every speaker so heads stay
        # proportionate and the sprites sit at the same height behind the box.
        pixel_scale = min(pixel_scale,
                          max(1, min(sprite_bottom, width) // portrait.get_height()))
        sprite = pygame.transform.scale(
            portrait, (portrait.get_width() * pixel_scale,
                       portrait.get_height() * pixel_scale))
        x = round(4 * width / 192)
        y = sprite_bottom - sprite.get_height()
        app.window.blit(sprite, (x, y))
    box = pygame.Rect(20, 76, 152, 27)
    _pixel_panel(app.canvas, box, DIALOGUE_FACE)
    nameplate = pygame.Rect(22, 67, 72, 10)
    _pixel_panel(app.canvas, nameplate, DIALOGUE_LABEL)
    app.text(title, (26, 72), anchor="midleft", small=True, larger=True, color=DIALOGUE_INK)
    for y, line in zip((81, 89, 97), lines):
        app.text(line, (23, y), anchor="midleft", small=True, larger=True, color=DIALOGUE_INK)
    # A small breathing advance marker replaces the modal's separate button.
    offset = int(app.elapsed * 2) % 2
    pygame.draw.polygon(app.canvas, ACCENT,
                        ((164, 101 + offset), (168, 101 + offset), (166, 103 + offset)))


def draw_loading(app) -> None:
    """Several cats chase, play with yarn, nap, and wake independently."""
    app.loading_cats.draw(app.canvas)


CUSTOMER_REPLY = pygame.Rect(119, 86, 48, 13)


def draw_customer(app, pointer: tuple[float, float]) -> None:
    """First order exchange, staged over the bakery with no customer sprite."""
    box = pygame.Rect(15, 63, 162, 42)
    _pixel_panel(app.canvas, box, DIALOGUE_FACE)
    nameplate = pygame.Rect(19, 56, 60, 9)
    _pixel_panel(app.canvas, nameplate, DIALOGUE_LABEL)
    app.text('MILA', (24, 60), anchor='midleft', small=True, larger=True,
             color=DIALOGUE_INK)
    if app.customer_step == 0:
        app.text('Hello! Is the cafe open?', (22, 73), anchor='midleft', small=True,
                 larger=True, color=DIALOGUE_INK)
        app.text('I could use something warm.', (22, 81), anchor='midleft', small=True,
                 larger=True, color=DIALOGUE_INK)
        app.button(CUSTOMER_REPLY, 'WELCOME IN', pointer)
    else:
        app.text('A house latte in a ceramic mug,', (22, 73), anchor='midleft',
                 small=True, larger=True, color=DIALOGUE_INK)
        app.text('and a croissant, please.', (22, 81), anchor='midleft',
                 small=True, larger=True, color=DIALOGUE_INK)
        app.button(CUSTOMER_REPLY, 'TAKE ORDER', pointer)


def draw_no_save(app, pointer: tuple[float, float]) -> None:
    app.popup(pygame.Rect(32, 32, 128, 49))
    app.text("NO SAVED GAME", (96, 43), title=True)
    app.text("START A NEW GAME?", (96, 55))
    app.button(pygame.Rect(46, 63, 45, 12), "NEW", pointer)
    app.button(pygame.Rect(101, 63, 45, 12), "BACK", pointer)


PAUSE_BUTTONS = {
    "resume": pygame.Rect(62, 45, 68, 12),
    "save": pygame.Rect(62, 61, 68, 12),
    "menu": pygame.Rect(62, 77, 68, 12),
}


def draw_pause(app, pointer: tuple[float, float]) -> None:
    app.popup(pygame.Rect(47, 19, 98, 78))
    app.text("PAUSED", (96, 31), title=True)
    pygame.draw.line(app.canvas, INK, (57, 38), (135, 38))
    app.button(PAUSE_BUTTONS["resume"], "RESUME", pointer)
    app.button(PAUSE_BUTTONS["save"], "SAVE GAME", pointer)
    app.button(PAUSE_BUTTONS["menu"], "MAIN MENU", pointer)
    if app.message and app.elapsed < app.message_until:
        app.text(app.message, (96, 94), small=True, color=ACCENT)
