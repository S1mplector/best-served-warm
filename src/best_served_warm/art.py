"""Load still art and frames rendered by pikupiku."""
from PIL import Image, ImageSequence
import pygame
from .paths import asset_path


def load_image(*parts: str) -> pygame.Surface:
    return pygame.image.load(str(asset_path(*parts))).convert_alpha()


class AnimatedButton:
    def __init__(self, name: str, center: tuple[int, int], width: int = 326):
        original = Image.open(asset_path("buttons", name + ".png")).convert("RGBA")
        gif = Image.open(asset_path("buttons", name + ".gif"))
        mask = original.getchannel("A").resize(gif.size, Image.Resampling.LANCZOS)
        self.frames = []
        for frame in ImageSequence.Iterator(gif):
            rgba = frame.convert("RGBA")
            rgba.putalpha(mask)
            surface = pygame.image.frombytes(rgba.tobytes(), rgba.size, "RGBA").convert_alpha()
            bounds = surface.get_bounding_rect(min_alpha=16)
            surface = surface.subsurface(bounds).copy()
            height = round(surface.get_height() * width / surface.get_width())
            self.frames.append(pygame.transform.smoothscale(surface, (width, height)))
        self.rect = self.frames[0].get_rect(center=center)
        self.phase = {"new-game": 0, "load-game": 1, "options": 2, "exit-game": 3}[name]

    def draw(self, screen: pygame.Surface, elapsed: float, hovered: bool) -> None:
        frame = self.frames[(int(elapsed * 6) + self.phase) % len(self.frames)]
        scale = 1.045 if hovered else 1.0
        if scale != 1.0:
            frame = pygame.transform.smoothscale(frame, (round(frame.get_width()*scale), round(frame.get_height()*scale)))
        screen.blit(frame, frame.get_rect(center=self.rect.center))
