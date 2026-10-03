"""Pixel-art cafe menu with low-resolution art and a crisp text overlay."""

from __future__ import annotations

import pygame

from .art import Cursor
from .cat import MenuCat
from .dialogue import Dialogue
from .menu import MENU_SIZE, NativeMenu
from .paths import asset_path
from .music import Music
from .sfx import SoundEffects
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
        scene_image = pygame.image.load(str(asset_path("images", "new_game_background.png"))).convert()
        self.scene_background = pygame.transform.scale(scene_image, MENU_SIZE)
        self.text_layer = pygame.Surface(self.window.get_size(), pygame.SRCALPHA)
        self.clock = pygame.time.Clock()
        # Rasterize the pixel font once; enlarge glyphs only by whole-number factors.
        self.font = pygame.font.Font(str(asset_path("fonts", "m5x7.ttf")), 32)
        self.heading = pygame.font.Font(str(asset_path("fonts", "m5x7.ttf")), 32)
        self.dialogue_font = pygame.font.Font(str(asset_path("fonts", "m5x7.ttf")), 16)
        self.menu = NativeMenu()
        self.cursor = Cursor(width=30)
        self.cat = MenuCat()
        pygame.mouse.set_visible(False)
        self.music = Music()
        self.music.set_volume(self.options["volume"])
        self.sfx = SoundEffects()
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
             color: tuple[int, int, int] = DARK, anchor: str = "center", small: bool = False,
             larger: bool = False) -> None:
        font = self.dialogue_font if small else self.heading if title else self.font
        glyphs = font.render(value, False, color)
        width, height = self.window.get_size()
        scale = max(1, int(min(width / (MENU_SIZE[0] * TEXT_SCALE),
                               height / (MENU_SIZE[1] * TEXT_SCALE))))
        if larger:
            scale += 1
        if scale > 1:
            glyphs = pygame.transform.scale(glyphs, (glyphs.get_width() * scale,
                                                      glyphs.get_height() * scale))
        position = (round(center[0] * width / MENU_SIZE[0]),
                    round(center[1] * height / MENU_SIZE[1]))
        rect = glyphs.get_rect(**{anchor: position})
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
        self.state = "intro_scene"

    def click(self, point: tuple[float, float]) -> None:
        self.sfx.click(self.state, point)
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
            if pygame.Rect(38, 94, 116, 10).collidepoint(x, y):
                self.options['typing_volume'] = round((self.options['typing_volume'] + 0.25) % 1.25, 2)
                self.sfx.typing(self.options['typing_volume'])
                save_options(self.options)
            elif pygame.Rect(39, 47, 114, 11).collidepoint(x, y):
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
        elif self.state == "intro_scene":
            self.state = "dialogue"
        elif self.state == "dialogue":
            if self.dialogue.advance():
                self.state = "menu"

    def draw(self) -> None:
        pointer = self.pointer(pygame.mouse.get_pos())
        self.sfx.hover(self.state, pointer)
        if self.text_layer.get_size() != self.window.get_size():
            self.text_layer = pygame.Surface(self.window.get_size(), pygame.SRCALPHA)
        self.text_layer.fill((0, 0, 0, 0))
        if self.state == "menu":
            self.menu.draw(self.canvas, pointer, self.frame_dt)
            self.cat.draw(self.canvas, self.frame_dt)
        elif self.state == "intro_scene":
            self.canvas.blit(self.scene_background, (0, 0))
        else:
            self.canvas.blit(self.menu.base, (0, 0))
            if self.state == "options":
                draw_options(self, pointer)
            elif self.state == "no_save":
                draw_no_save(self, pointer)
            else:
                draw_dialogue(self, pointer)
        pygame.transform.scale(self.canvas, self.window.get_size(), self.window)
        self.window.blit(self.text_layer, (0, 0))
        if pygame.mouse.get_focused():
            self.cursor.draw(self.window, *pygame.mouse.get_pos(), self.elapsed,
                             self.state == "menu" and self.menu.button_at(pointer) is not None)
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self.frame_dt = min(self.clock.tick(60) / 1000, 0.1)
            self.elapsed += self.frame_dt
            if self.state == 'dialogue' and self.dialogue.update(self.frame_dt):
                self.sfx.typing(self.options['typing_volume'])
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.click(self.pointer(event.pos))
                elif (event.type == pygame.KEYDOWN and self.state in ("intro_scene", "dialogue")
                      and event.key in (pygame.K_SPACE, pygame.K_RETURN)):
                    self.sfx.play("advance")
                    if self.state == "intro_scene":
                        self.state = "dialogue"
                    elif self.dialogue.advance():
                        self.state = "menu"
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state != "menu":
                        self.sfx.play("back")
                    if self.state in ("menu", "intro_scene", "dialogue"):
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
