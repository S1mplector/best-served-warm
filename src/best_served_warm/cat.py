"""A small autonomous cat: stroll, rest, and hop between menu platforms."""
import random
import pygame
from .art import load_image
from .menu import BUTTON_RECTS


class MenuCat:
    FLOOR = 107
    SPEED = 17

    def __init__(self, seed=None):
        self.random = random.Random(seed)
        sheet = load_image('cat', 'grey-walk.png')
        self.frames = [sheet.subsurface((i * 16, 0, 16, 16)).copy() for i in range(4)]
        rest_sheet = load_image('cat', 'grey-rest.png')
        self.rest_frames = [rest_sheet.subsurface((i * 16, 0, 16, 16)).copy() for i in range(4)]
        self.nap_cooldown = 5.0
        self.x, self.feet = 28.0, float(self.FLOOR)
        self.facing = 1
        self.state = 'walk'
        self.target = 65.0
        self.timer = 0.0
        self.age = 0.0
        self.platform = None

    def choose(self):
        self.timer = 0.0
        if self.nap_cooldown <= 0 and self.random.random() < 0.25:
            self.state = 'settle'
            self.timer = 0.8
            return
        # Reach nearby button tops one at a time; occasionally return to the floor.
        reachable = [(name, rect) for name, rect in BUTTON_RECTS.items()
                     if name != self.platform and 0 < self.feet - rect.top <= 20
                     and abs(self.x - rect.centerx) < 55]
        if reachable and self.random.random() < 0.65:
            name, rect = self.random.choice(reachable)
            self.jump_to(self.random.uniform(rect.left + 9, rect.right - 9), rect.top, name)
        elif self.platform is not None:
            if self.random.random() < 0.55:
                self.jump_to(self.random.choice((57, 139)), self.FLOOR, None)
            else:
                self.rest()
        elif self.random.random() < 0.3:
            self.rest()
        else:
            self.state = 'walk'
            self.target = self.random.uniform(12, 180)

    def rest(self):
        self.state = 'rest'
        self.timer = self.random.uniform(0.7, 2.3)

    def jump_to(self, x, feet, platform):
        self.state = 'jump'
        self.start = (self.x, self.feet)
        self.landing = (x, float(feet))
        self.next_platform = platform
        self.timer = 0.0
        self.facing = 1 if x >= self.x else -1

    def update(self, dt):
        self.age += dt
        self.nap_cooldown = max(0.0, self.nap_cooldown - dt)
        if self.state in ('settle', 'sleep', 'wake'):
            self.timer -= dt
            if self.timer <= 0:
                if self.state == 'settle':
                    self.state = 'sleep'
                    self.timer = self.random.uniform(6.0, 14.0)
                elif self.state == 'sleep':
                    self.state = 'wake'
                    self.timer = 1.0
                    self.nap_cooldown = self.random.uniform(18.0, 35.0)
                else:
                    self.choose()
            return
        if self.state == 'walk':
            distance = self.target - self.x
            self.facing = 1 if distance >= 0 else -1
            if abs(distance) <= self.SPEED * dt:
                self.x = self.target
                self.rest()
            else:
                self.x += self.facing * self.SPEED * dt
        elif self.state == 'rest':
            self.timer -= dt
            if self.timer <= 0:
                self.choose()
        elif self.state == 'jump':
            self.timer += dt
            t = min(1.0, self.timer / 0.7)
            self.x = self.start[0] + (self.landing[0] - self.start[0]) * t
            self.feet = self.start[1] + (self.landing[1] - self.start[1]) * t - 4 * 18 * t * (1 - t)
            if t == 1:
                self.platform = self.next_platform
                self.rest()

    def draw(self, screen, dt):
        self.update(dt)
        index = int(self.age * 7) % 4 if self.state == 'walk' else 0
        frame = self.frames[index]
        if self.state == 'settle':
            frame = self.rest_frames[min(3, int((0.8 - self.timer) * 5))]
        elif self.state == 'sleep':
            frame = self.rest_frames[3]
        elif self.state == 'wake':
            frame = self.rest_frames[max(0, min(3, int(self.timer * 4)))]
        # Source side-view frames face left; flip only to face right.
        if self.facing > 0:
            frame = pygame.transform.flip(frame, True, False)
        bottom = frame.get_bounding_rect().bottom
        screen.blit(frame, (round(self.x) - 8, round(self.feet) - bottom))
        if self.state == 'sleep':
            # A tiny floating Z makes quiet naps readable without moving the paws.
            x = round(self.x) + 5
            y = round(self.feet) - 12 - int(self.age % 2)
            pygame.draw.lines(screen, (137, 87, 67), False,
                              ((x, y), (x + 3, y), (x, y + 3), (x + 3, y + 3)))
