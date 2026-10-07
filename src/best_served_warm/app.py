"""Pixel-art cafe menu with low-resolution art and a crisp text overlay."""

from __future__ import annotations

import pygame

from .art import Cursor
from .cat import MenuCat
from .coffee_station import CoffeeStation, STATION_SIZE
from .coffee import Coffee
from .station_view import StationView
from .stations import Kitchen, Cup, Portafilter
from .loading_cats import LoadingCats
from .dialogue import DIALOGUE, Dialogue
from .menu import MENU_SIZE, NativeMenu
from .paths import asset_path
from .music import Music
from .sfx import SoundEffects
from .screens import ACCENT, DARK, HOVER, INK, PAPER, SHADOW
from .screens import PAUSE_BUTTONS, CUSTOMER_REPLY, draw_customer, draw_dialogue, draw_loading, draw_options, draw_no_save, draw_pause
from .storage import DEFAULT_GAME, load_game, load_options, save_game, save_options

TEXT_SCALE = 3
class App:
    def __init__(self) -> None:
        pygame.init()
        self.options = load_options()
        self.window = self._set_window()
        pygame.display.set_caption("Best Served Warm")
        self.canvas = pygame.Surface(MENU_SIZE).convert_alpha()
        self.scene_background = pygame.image.load(str(asset_path("images", "new_game_background.png"))).convert()
        self.scene_window = pygame.transform.scale(self.scene_background, self.window.get_size())
        self.scene_window_size = self.window.get_size()
        self.station_background = pygame.image.load(str(asset_path("images", "coffee_cup_station.png"))).convert()
        self.station_window = pygame.transform.scale(self.station_background, self.window.get_size())
        self.station_window_size = self.window.get_size()
        self.station_overlay = pygame.Surface(STATION_SIZE, pygame.SRCALPHA)
        self.coffee_station = CoffeeStation()
        self.loading_cat = pygame.image.load(str(asset_path("cat", "white-sleep.png"))).convert_alpha()
        self.lena_portrait = pygame.image.load(str(asset_path("characters", "lena.png"))).convert_alpha()
        self.sam_portrait = pygame.image.load(str(asset_path("characters", "sam.png"))).convert_alpha()
        self.heather_portrait = pygame.image.load(str(asset_path("characters", "mrs_heather.png"))).convert_alpha()
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
        self.paused_from = "dialogue"
        self.dialogue = Dialogue()
        self.customer_step = 0
        self.coffee = Coffee()
        self.kitchen = Kitchen()
        self.workbench = StationView(self)
        self.loading_cats = LoadingCats()
        self.message = ""
        self.message_until = 0.0
        self.elapsed = 0.0
        self.loading_elapsed = 0.0
        self.loading_target = "intro_scene"
        self.scene_fade = 1.0
        self.frame_dt = 0.0
        self.running = True

    def _set_window(self) -> pygame.Surface:
        if self.options["fullscreen"]:
            return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        return pygame.display.set_mode((1152, 648), pygame.RESIZABLE)

    def pointer(self, screen_pos: tuple[int, int]) -> tuple[float, float]:
        width, height = self.window.get_size()
        return screen_pos[0] * MENU_SIZE[0] / width, screen_pos[1] * MENU_SIZE[1] / height

    def station_pointer(self, point: tuple[float, float]) -> tuple[float, float]:
        return point[0] * STATION_SIZE[0] / MENU_SIZE[0], point[1] * STATION_SIZE[1] / MENU_SIZE[1]

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
        self.coffee = Coffee()
        self.workbench.cancel_hold()
        self.kitchen = Kitchen()
        self.customer_step = 0
        self.coffee_station = CoffeeStation()
        self.loading_cats = LoadingCats()
        self.workbench.category = 'milk'
        # This chapter is text-only: go straight to the cafe background and
        # avoid the loading, cup-station, and coffee gameplay flow.
        self.loading_elapsed = 0.0
        self.scene_fade = 1.0
        self.state = "dialogue"

    def start_cup_station(self) -> None:
        self.loading_elapsed = 0.0
        self.loading_target = 'cup_station'
        self.scene_fade = 0.0
        self.coffee_station = CoffeeStation()
        self.state = 'loading'

    def accept_cup(self) -> None:
        if not self.coffee_station.placed:
            return
        selected = self.coffee_station.placed[-1]
        vessel = {'mug':'mug', 'cold':'tall', 'takeaway':'mug'}[selected['style']]
        key = self.kitchen.take_cup(vessel)
        self.kitchen.place('espresso')
        self.kitchen.cups[key].style = selected['style']
        self.kitchen.cups[key].size = selected['size']
        self.workbench.station = 'grinder'
        self.state = 'coffee'

    def save_progress(self) -> None:
        scene = self.paused_from
        game = DEFAULT_GAME.copy()
        game.update(scene=scene, page=self.dialogue.page,
                    revealed=self.dialogue.revealed)
        if scene == 'coffee':
            game['kitchen'] = self.kitchen.to_dict()
        elif scene == 'customer':
            game['customer_step'] = self.customer_step
        elif scene == 'cup_station':
            game['cup_station'] = self.coffee_station.to_dict()
        try:
            save_game(game)
            self.message = "GAME SAVED"
        except OSError:
            self.message = "SAVE FAILED - TRY AGAIN"
        self.message_until = self.elapsed + 2.0

    def load_progress(self) -> bool:
        game = load_game()
        if game is None:
            return False
        self.dialogue = Dialogue()
        self.dialogue.page = min(game.get("page", 0), len(DIALOGUE) - 1)
        self.dialogue.revealed = min(game.get("revealed", 0.0),
                                     sum(map(len, self.dialogue.current[1:])))
        self.scene_fade = 1.0
        self.coffee = Coffee.from_dict(game['coffee']) if 'coffee' in game else Coffee()
        self.workbench.cancel_hold()
        self.kitchen = Kitchen.from_dict(game['kitchen']) if 'kitchen' in game else Kitchen()
        self.customer_step = game.get('customer_step', 0)
        self.coffee_station = CoffeeStation()
        if 'cup_station' in game:
            self.coffee_station.restore(game['cup_station'])
        if 'coffee' in game:
            old = self.coffee
            self.kitchen = Kitchen(served=old.served, earnings=old.earnings, order_index=old.order_index)
            if old.vessel and old.stage != 5:
                self.kitchen.cups['cup_1'] = Cup('finish' if old.brew else 'espresso',old)
                self.kitchen.next_id = 2
                self.kitchen.filter = Portafilter(location='espresso' if old.tamped else 'grinder',
                    beans=old.beans or 'medium',grind_size=old.grind_size,dose=old.grind*18,
                    pressure=old.tamp_pressure,tamped=old.tamped,dirty=old.brew>0)
        self.workbench.station = 'shelf'
        self.workbench.category = 'milk'
        self.state = game.get("scene", "dialogue")
        return True

    def click(self, point: tuple[float, float]) -> None:
        self.sfx.click(self.state, point)
        x, y = point
        if self.state == "menu":
            action = self.menu.button_at(point)
            if action == "new":
                self.start_dialogue()
            elif action == "load":
                if not self.load_progress():
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
        elif self.state == "pause":
            if PAUSE_BUTTONS["resume"].collidepoint(x, y):
                self.state = self.paused_from
            elif PAUSE_BUTTONS["save"].collidepoint(x, y):
                self.save_progress()
            elif PAUSE_BUTTONS["menu"].collidepoint(x, y):
                self.state = "menu"
        elif self.state == "intro_scene":
            if self.scene_fade >= 1.0:
                self.state = "dialogue"
        elif self.state == 'loading' and self.loading_elapsed >= .4:
            self.state = self.loading_target
        elif self.state == 'customer':
            if CUSTOMER_REPLY.collidepoint(x, y):
                if self.customer_step == 0:
                    self.customer_step = 1
                else:
                    self.start_cup_station()
        elif self.state == 'cup_station':
            if self.coffee_station.placed and pygame.Rect(73, 94, 47, 12).collidepoint(x, y):
                self.accept_cup()
            elif self.scene_fade >= 1.0:
                self.coffee_station.click(self.station_pointer(point))
        elif self.state == "dialogue":
            self.dialogue.advance()

    def draw(self) -> None:
        pointer = self.pointer(pygame.mouse.get_pos())
        self.sfx.hover(self.state, pointer)
        if self.text_layer.get_size() != self.window.get_size():
            self.text_layer = pygame.Surface(self.window.get_size(), pygame.SRCALPHA)
        self.text_layer.fill((0, 0, 0, 0))
        if self.state == "menu":
            self.menu.draw(self.canvas, pointer, self.frame_dt)
            self.cat.draw(self.canvas, self.frame_dt)
        elif self.state == "loading":
            draw_loading(self)
        elif self.state == 'coffee' or (self.state == 'pause' and self.paused_from == 'coffee'):
            self.workbench.draw(self.workbench.pointer(pygame.mouse.get_pos()))
            if self.state == 'pause':
                self.window.blit(self.text_layer, (0, 0))
                self.text_layer.fill((0, 0, 0, 0))
                self.canvas.fill((0, 0, 0, 0))
                draw_pause(self, pointer)
                self.window.blit(pygame.transform.scale(self.canvas, self.window.get_size()), (0, 0))
        elif self.state in ('intro_scene','customer','dialogue','cup_station','pause'):
            window_size = self.window.get_size()
            cup_scene = self.state == 'cup_station' or (self.state == 'pause' and self.paused_from == 'cup_station')
            if cup_scene:
                if self.station_window_size != window_size:
                    self.station_window = pygame.transform.scale(self.station_background, window_size)
                    self.station_window_size = window_size
                self.window.blit(self.station_window, (0, 0))
                overlay = self.coffee_station.draw(self.station_pointer(pointer))
                self.window.blit(pygame.transform.scale(overlay, window_size), (0, 0))
                if self.state == 'cup_station':
                    if self.coffee_station.placed:
                        self.canvas.fill((0, 0, 0, 0))
                        self.button(pygame.Rect(73,94,47,12), 'NEXT STATION', pointer)
                        self.window.blit(pygame.transform.scale(self.canvas, window_size), (0, 0))
                    else:
                        self.text('CHOOSE A CUP, THEN PLACE IT', (96,102), small=True, color=(251,224,187))
            else:
                if self.scene_window_size != window_size:
                    self.scene_window = pygame.transform.scale(self.scene_background, window_size)
                    self.scene_window_size = window_size
                self.window.blit(self.scene_window, (0, 0))
            if self.state in ('dialogue','customer'):
                self.canvas.fill((0,0,0,0))
                if self.state == 'customer': draw_customer(self, pointer)
                else: draw_dialogue(self, pointer)
                self.window.blit(pygame.transform.scale(self.canvas, window_size), (0,0))
            elif self.state == 'pause':
                self.canvas.fill((0,0,0,0))
                draw_pause(self, pointer)
                self.window.blit(pygame.transform.scale(self.canvas, window_size), (0,0))
            elif self.scene_fade < 1.0:
                fade=pygame.Surface(window_size)
                fade.fill((0,0,0))
                fade.set_alpha(round(255*(1-self.scene_fade)))
                self.window.blit(fade,(0,0))
        else:
            self.canvas.blit(self.menu.base, (0, 0))
            if self.state == "options":
                draw_options(self, pointer)
            elif self.state == "no_save":
                draw_no_save(self, pointer)
        if self.state not in ('intro_scene','customer','dialogue','cup_station','pause','coffee'):
            pygame.transform.scale(self.canvas, self.window.get_size(), self.window)
        self.window.blit(self.text_layer, (0, 0))
        if pygame.mouse.get_focused() and self.state != "loading":
            self.cursor.draw(self.window, *pygame.mouse.get_pos(), self.elapsed,
                             self.state == "menu" and self.menu.button_at(pointer) is not None)
        pygame.display.flip()

    def handle_event(self, event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == 'coffee':
                self.workbench.press(self.workbench.pointer(event.pos))
            else:
                self.click(self.pointer(event.pos))
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.state == 'coffee':
                self.workbench.release()
        elif event.type == pygame.WINDOWFOCUSLOST:
            self.workbench.cancel_hold()
        elif (event.type == pygame.KEYDOWN and self.state in ("intro_scene", "dialogue", "customer")
              and event.key in (pygame.K_SPACE, pygame.K_RETURN)):
            self.sfx.play("advance")
            if self.state == "intro_scene":
                if self.scene_fade >= 1.0:
                    self.state = "dialogue"
            elif self.state == 'customer':
                if self.customer_step == 0: self.customer_step = 1
                else: self.start_cup_station()
            else:
                self.dialogue.advance()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.state != "menu":
                self.sfx.play("back")
            if self.state in ("intro_scene", "dialogue", "customer", "cup_station", "coffee"):
                self.workbench.cancel_hold()
                self.paused_from = self.state
                self.message = ""
                self.state = "pause"
            elif self.state == "pause":
                self.state = self.paused_from
            elif self.state in ("menu", "loading"):
                self.state = "menu"
            else:
                if self.state == "options":
                    save_options(self.options)
                self.state = "menu"

    def run(self) -> None:
        while self.running:
            self.frame_dt = min(self.clock.tick(60) / 1000, 0.1)
            self.elapsed += self.frame_dt
            if self.state == "loading":
                self.loading_elapsed += self.frame_dt
                self.loading_cats.update(self.frame_dt)
                if self.loading_elapsed >= 3.2:
                    self.state = self.loading_target
                    self.scene_fade = 0.0
            elif self.state in ("intro_scene", "cup_station"):
                self.scene_fade = min(1.0, self.scene_fade + self.frame_dt / 1.35)
            if self.state == 'dialogue' and self.dialogue.update(self.frame_dt):
                self.sfx.typing(self.options['typing_volume'])
            if self.state == 'coffee':
                self.workbench.update(self.frame_dt, self.workbench.pointer(pygame.mouse.get_pos()))
            for event in pygame.event.get():
                self.handle_event(event)
            self.draw()
        self.music.close()
        pygame.mouse.set_visible(True)
        pygame.quit()


def main() -> None:
    App().run()
