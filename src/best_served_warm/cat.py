"""Small native-resolution animated decor for the main menu."""
from PIL import Image
import pygame
from .paths import asset_path

class MenuCat:
    """Tiny 16x16 walk cycle that wanders along the menu's clear outer edge."""

    def __init__(self):
        source = Image.open(asset_path("cat", "grey-walk.png")).convert("RGBA")
        self.frames = []
        for index in range(4):
            crop = source.crop((index * 16, 4 * 16, (index + 1) * 16, 5 * 16))
            self.frames.append(pygame.image.frombytes(crop.tobytes(), crop.size, "RGBA").convert_alpha())
        # Keep the cat near the frame edges, clear of button labels.
        self.path = ((7, 13), (27, 13), (42, 13), (27, 13), (7, 13),
                     (7, 25), (7, 83), (7, 96), (27, 96), (42, 96),
                     (27, 96), (7, 96), (7, 83), (7, 25))

    def draw(self, screen: pygame.Surface, elapsed: float) -> None:
        segment_time = 1.6
        cycle = elapsed / segment_time
        index = int(cycle) % len(self.path)
        progress = cycle - int(cycle)
        start = self.path[index]
        end = self.path[(index + 1) % len(self.path)]
        x = round(start[0] + (end[0] - start[0]) * progress)
        y = round(start[1] + (end[1] - start[1]) * progress)
        frame = self.frames[int(elapsed * 6) % len(self.frames)]
        if end[0] < start[0]:
            frame = pygame.transform.flip(frame, True, False)
        screen.blit(frame, (x, y))
