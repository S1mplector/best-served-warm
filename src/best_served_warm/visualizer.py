"""Smooth audio levels; draw repeated copies of one bar image."""
import math
import numpy as np
import pygame
from .art import load_image


class Visualizer:
    def __init__(self):
        raw = load_image("images", "bar.png")
        self.sprite = raw.subsurface(raw.get_bounding_rect(min_alpha=32)).copy()
        self.smoothed = np.zeros(28, dtype=np.float32)
        self.scaled = {}

    def update(self, target: np.ndarray, dt: float) -> None:
        for i in range(len(self.smoothed)):
            speed = 12.0 if target[i] > self.smoothed[i] else 4.2
            alpha = 1.0 - math.exp(-speed * min(dt, 0.1))
            self.smoothed[i] += (target[i] - self.smoothed[i]) * alpha

    def draw(self, screen: pygame.Surface, x: int, bottom: int, elapsed: float, enabled: bool = True) -> None:
        if not enabled:
            return
        for i, value in enumerate(self.smoothed):
            height = max(12, round(16 + 84 * float(value)))
            # Quantizing dimensions keeps the sprite cache small without making motion jerky.
            height = 2 * round(height / 2)
            key = (9, height)
            if key not in self.scaled:
                self.scaled[key] = pygame.transform.smoothscale(self.sprite, key)
            bar = self.scaled[key]
            screen.blit(bar, (x+i*12, bottom-height))
