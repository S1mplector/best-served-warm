"""Pixel-art cafe menu with low-resolution art and a crisp text overlay."""

from __future__ import annotations

import pygame

from .art import AnimatedCursor
from .cat import MenuCat
from .dialogue import Dialogue
from .menu import MENU_SIZE, NativeMenu
from .music import Music
from .screens import ACCENT, DARK, HOVER, INK, PAPER, SHADOW
from .screens import draw_dialogue, draw_options, draw_no_save
from .storage import load_options, save_options

TEXT_SCALE = 3
class App:
    def __init__(self) -> None:
        pygame.init()
        self.options = load_options()
        self.window = self._set_window()
        pygame.display.set_caption("Best Served Warm")
        self.canvas = pygame.Surface(MENU_SIZE).convert_alpha()
        self.text_layer = pygame.Surface((MENU_SIZE[0] * TEXT_SCALE, MENU_SIZE[1] * TEXT_SCALE), pygame.SRCALPHA)
        self.frame = pygame.Surface(self.text_layer.get_size()).convert_alpha()
        self.clock = pygame.time.Clock()
        # Render glyphs at 3x the art resolution, then composite over nearest-neighbour pixels.
        self.font = pygame.font.Font(None, 30)
        self.heading = pygame.font.Font(None, 36)
        self.menu = NativeMenu()
        self.cursor = AnimatedCursor(width=10)
        self.cat = MenuCat()
        pygame.mouse.set_visible(False)
        self.music = Music()
        self.music.set_volume(self.options["volume"])
        self.state = "menu"
        self.dialogue = Dialogue()
        self.message = ""
        self.message_until = 0.0
        self.elapsed = 0.0
        self.frame_dt = 0.0
        self.running = True

    def _set_window(self) -> pygame.Surface:
        if self.options["fullscreen"]:
            return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        return pygame.display.set_mode((1152, 648), pygame.RESIZABLE)

    def pointer(self, screen_pos: tuple[int, int]) -> tuple[float, float]:
        width, height = self.window.get_size()
        return screen_pos[0] * MENU_SIZE[0] / width, screen_pos[1] * MENU_SIZE[1] / height

    def text(self, value: str, center: tuple[int, int], *, title: bool = False,
             color: tuple[int, int, int] = DARK) -> None:
        font = self.heading if title else self.font
        glyphs = font.render(value, False, color)
        rect = glyphs.get_rect(center=(center[0] * TEXT_SCALE, center[1] * TEXT_SCALE))
        self.text_layer.blit(glyphs, rect)

    def popup(self, rect: pygame.Rect) -> None:
        shade = pygame.Surface(MENU_SIZE, pygame.SRCALPHA)
        shade.fill((74, 42, 35, 65))
        self.canvas.blit(shade, (0, 0))
        pygame.draw.rect(self.canvas, SHADOW, rect.move(2, 2))
        pygame.draw.rect(self.canvas, DARK, rect)
        pygame.draw.rect(self.canvas, PAPER, rect.inflate(-2, -2))
        pygame.draw.line(self.canvas, (255, 255, 255),
                         (rect.left + 2, rect.top + 2), (rect.right - 3, rect.top + 2))

    def button(self, rect: pygame.Rect, value: str, pointer: tuple[float, float]) -> None:
        hovered = rect.collidepoint(pointer)
        fill = (255, 221, 185) if hovered else HOVER
        pygame.draw.rect(self.canvas, SHADOW, rect.move(1, 1))
        pygame.draw.rect(self.canvas, INK, rect)
        pygame.draw.rect(self.canvas, fill, rect.inflate(-2, -2))
        self.text(value, rect.center, color=ACCENT if hovered else DARK)

    def start_dialogue(self) -> None:
        self.dialogue = Dialogue()
        self.state = "dialogue"

    def click(self, point: tuple[float, float]) -> None:
        x, y = point
        if self.state == "menu":
            action = self.menu.button_at(point)
            if action == "new":
                self.start_dialogue()
            elif action == "load":
                self.state = "no_save"
            elif action == "options":
                self.state = "options"
            elif action == "exit":
                self.running = False
        elif self.state == "options":
            if pygame.Rect(39, 47, 114, 11).collidepoint(x, y):
                self.options["volume"] = round(max(0.0, min(1.0, (x - 39) / 113)), 2)
                self.music.set_volume(self.options["volume"])
            elif pygame.Rect(120, 60, 34, 13).collidepoint(x, y):
                self.options["fullscreen"] = not self.options["fullscreen"]
                self.window = self._set_window()
            elif pygame.Rect(68, 79, 56, 13).collidepoint(x, y):
                save_options(self.options)
                self.state = "menu"
        elif self.state == "no_save":
            if pygame.Rect(46, 63, 45, 12).collidepoint(x, y):
                self.start_dialogue()
            elif pygame.Rect(101, 63, 45, 12).collidepoint(x, y):
                self.state = "menu"
        elif self.state == "dialogue":
            if self.dialogue.advance():
                self.state = "menu"

    def draw(self) -> None:
        pointer = self.pointer(pygame.mouse.get_pos())
        self.text_layer.fill((0, 0, 0, 0))
        if self.state == "menu":
            self.menu.draw(self.canvas, pointer, self.frame_dt)
            self.cat.draw(self.canvas, self.elapsed)
        else:
            self.canvas.blit(self.menu.base, (0, 0))
            if self.state == "options":
                draw_options(self, pointer)
            elif self.state == "no_save":
                draw_no_save(self, pointer)
            else:
                draw_dialogue(self, pointer)
        if 0 <= pointer[0] < MENU_SIZE[0] and 0 <= pointer[1] < MENU_SIZE[1]:
            self.cursor.draw(self.canvas, *pointer, self.elapsed, self.state == "menu" and self.menu.button_at(pointer) is not None)
        pygame.transform.scale(self.canvas, self.frame.get_size(), self.frame)
        self.frame.blit(self.text_layer, (0, 0))
        pygame.transform.scale(self.frame, self.window.get_size(), self.window)
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self.frame_dt = min(self.clock.tick(60) / 1000, 0.1)
            self.elapsed += self.frame_dt
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.click(self.pointer(event.pos))
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state in ("menu", "dialogue"):
                        self.state = "menu"
                    else:
                        if self.state == "options":
                            save_options(self.options)
                        self.state = "menu"
            self.draw()
        self.music.close()
        pygame.mouse.set_visible(True)
        pygame.quit()


def main() -> None:
    App().run()
