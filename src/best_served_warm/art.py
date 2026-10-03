"""Load still art and frames rendered by the in-project Python line-boil tool."""
from PIL import Image, ImageFilter, ImageSequence
import pygame
from .paths import asset_path


def load_image(*parts: str) -> pygame.Surface:
    return pygame.image.load(str(asset_path(*parts))).convert_alpha()


class AnimatedButton:
    def __init__(self, name: str, center: tuple[int, int], width: int = 100):
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
        self.back = [pygame.transform.scale(load_image("ui", "cozy_starter", file), (128, 48))
                     for file in ("button_wide_normal.png", "button_wide_pressed.png")]
        self.rect = self.back[0].get_rect(center=center)
        self.phase = {"new-game": 0, "load-game": 1, "options": 2, "exit-game": 3}[name]
        self.hover_amount = 0.0
        self.last_elapsed = 0.0


    def draw(self, screen: pygame.Surface, elapsed: float, hovered: bool) -> None:
        frame = self.frames[(int(elapsed * 5) + self.phase) % len(self.frames)]
        delta = min(max(elapsed - self.last_elapsed, 0.0), 0.1)
        self.last_elapsed = elapsed
        target = 1.0 if hovered else 0.0
        self.hover_amount += (target - self.hover_amount) * min(1.0, delta * 8)
        eased = self.hover_amount * self.hover_amount * (3 - 2 * self.hover_amount)
        center = (self.rect.centerx, self.rect.centery + round(eased))
        screen.blit(self.back[1 if eased > 0.5 else 0], self.rect)
        screen.blit(frame, frame.get_rect(center=center))


class AnimatedLogo:
    """Display a softly animated logo with a diffused drop shadow."""

    def __init__(self, width: int = 225):
        original = Image.open(asset_path("images", "logo.png")).convert("RGBA")
        gif = Image.open(asset_path("images", "logo.gif"))
        mask = original.getchannel("A").resize(gif.size, Image.Resampling.LANCZOS)
        self.frames = []
        for frame in ImageSequence.Iterator(gif):
            rgba = frame.convert("RGBA")
            rgba.putalpha(mask)
            surface = pygame.image.frombytes(rgba.tobytes(), rgba.size, "RGBA").convert_alpha()
            surface = surface.subsurface(surface.get_bounding_rect(min_alpha=16)).copy()
            height = round(surface.get_height() * width / surface.get_width())
            self.frames.append(pygame.transform.smoothscale(surface, (width, height)))

        shadow_alpha = original.getchannel("A").filter(ImageFilter.GaussianBlur(18))
        shadow_alpha = shadow_alpha.point(lambda alpha: round(alpha * 0.4))
        shadow = Image.new("RGBA", original.size, (54, 31, 20, 0))
        shadow.putalpha(shadow_alpha)
        shadow_surface = pygame.image.frombytes(shadow.tobytes(), shadow.size, "RGBA").convert_alpha()
        shadow_height = round(shadow_surface.get_height() * width / shadow_surface.get_width())
        self.shadow = pygame.transform.smoothscale(shadow_surface, (width, shadow_height))

    def draw(self, screen: pygame.Surface, center: tuple[int, int], elapsed: float) -> None:
        frame = self.frames[int(elapsed * 5) % len(self.frames)]
        shadow_center = (center[0], center[1] + 5)
        screen.blit(self.shadow, self.shadow.get_rect(center=shadow_center))
        screen.blit(frame, frame.get_rect(center=center))


class AnimatedCursor:
    """Draw the selected 16x16 itch cursor sprites with a top-left hotspot."""

    def __init__(self, width: int = 16):
        self.arrow = load_image("cursor", "megabyte", "cursor-pointer-1.png")
        self.hand = load_image("cursor", "megabyte", "cursor-pointer-5.png")
        if width != 16:
            size = (width, width)
            self.arrow = pygame.transform.scale(self.arrow, size)
            self.hand = pygame.transform.scale(self.hand, size)

    def draw(self, screen: pygame.Surface, x: float, y: float, elapsed: float, hovered: bool) -> None:
        screen.blit(self.hand if hovered else self.arrow, (round(x), round(y)))
