"""Native-resolution interaction for the supplied 192x108 main-menu art."""

from __future__ import annotations

from PIL import Image
import pygame

from .paths import asset_path


MENU_SIZE = (192, 108)

# Bounds of the white button art, measured in IMG_6443.PNG's native pixels.
BUTTON_RECTS = {
    "new": pygame.Rect(76, 60, 44, 11),
    "load": pygame.Rect(76, 72, 44, 11),
    "options": pygame.Rect(76, 84, 44, 11),
    "exit": pygame.Rect(76, 95, 44, 11),
}


class NativeMenu:
    def __init__(self) -> None:
        image = Image.open(asset_path("images", "main_menu.png")).convert("RGBA")
        if image.size != MENU_SIZE:
            raise ValueError(f"main menu must be {MENU_SIZE}, got {image.size}")
        self.base = pygame.image.frombytes(image.tobytes(), image.size, "RGBA").convert_alpha()
        # Permanent title resident; never participates in the wandering AI.
        sleeper = pygame.image.load(str(asset_path("cat", "white-sleep.png"))).convert_alpha()
        feet = sleeper.get_bounding_rect().bottom
        self.base.blit(sleeper, (109, 23 - feet))
        self.hover = {action: 0.0 for action in BUTTON_RECTS}
        self.tiles: dict[str, list[pygame.Surface]] = {}
        for action, rect in BUTTON_RECTS.items():
            crop = image.crop((rect.left, rect.top, rect.right, rect.bottom))
            frames = []
            for step in range(7):
                frame = crop.copy()
                pixels = frame.load()
                strength = step / 6
                for y in range(frame.height):
                    for x in range(frame.width):
                        r, g, b, a = pixels[x, y]
                        # Only the white interior changes. Embedded letters,
                        # outlines, and the pixel shadow remain untouched.
                        if min(r, g, b) >= 235 and max(r, g, b) - min(r, g, b) <= 24:
                            target = (255, 244, 213)
                            pixels[x, y] = tuple(round(old + (new - old) * strength)
                                                 for old, new in zip((r, g, b), target)) + (a,)
                frames.append(pygame.image.frombytes(frame.tobytes(), frame.size, "RGBA").convert_alpha())
            self.tiles[action] = frames

    def button_at(self, point: tuple[float, float]) -> str | None:
        for action, rect in BUTTON_RECTS.items():
            if rect.collidepoint(point):
                return action
        return None

    def draw(self, surface: pygame.Surface, pointer: tuple[float, float], dt: float) -> None:
        surface.blit(self.base, (0, 0))
        active = self.button_at(pointer)
        for action, rect in BUTTON_RECTS.items():
            target = 1.0 if action == active else 0.0
            self.hover[action] += (target - self.hover[action]) * min(1.0, dt * 12)
            step = round(self.hover[action] * 6)
            if step:
                surface.blit(self.tiles[action][step], rect.topleft)
