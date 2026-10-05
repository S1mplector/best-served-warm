"""Quiet UI feedback, with entry-only hover sounds and bounded playback."""
import pygame
from .menu import BUTTON_RECTS
from .screens import PAUSE_BUTTONS
from .paths import asset_path


def target_at(state, point):
    targets = {
        'menu': BUTTON_RECTS,
        'options': {'typing': pygame.Rect(38, 94, 116, 10), 'volume': pygame.Rect(39, 47, 114, 11),
                    'toggle': pygame.Rect(120, 60, 34, 13),
                    'back': pygame.Rect(68, 79, 56, 13)},
        'no_save': {'new': pygame.Rect(46, 63, 45, 12),
                    'back': pygame.Rect(101, 63, 45, 12)},
        'pause': PAUSE_BUTTONS,
    }
    if state == 'dialogue':
        return 'advance'
    return next((name for name, rect in targets.get(state, {}).items()
                 if rect.collidepoint(point)), None)


class SoundEffects:
    FILES = {'hover': ('tick_001', 0.09), 'click': ('click_002', 0.22),
             'back': ('back_001', 0.12), 'toggle': ('switch_001', 0.15),
             'advance': ('select_001', 0.12)}

    def __init__(self):
        self.sounds = {}
        self.previous = None
        self.last_play = {}
        if pygame.mixer.get_init():
            for name, (file, volume) in self.FILES.items():
                sound = pygame.mixer.Sound(str(asset_path('audio', 'ui', file + '.ogg')))
                sound.set_volume(volume)
                self.sounds[name] = sound

    def typing(self, volume):
        if volume <= 0 or not pygame.mixer.get_init():
            return
        if 'type' not in self.sounds:
            self.sounds['type'] = pygame.mixer.Sound(str(asset_path('audio', 'ui', 'type.wav')))
        self.sounds['type'].set_volume(volume * 0.45)
        self.play('type')

    def play(self, name):
        now = pygame.time.get_ticks()
        if name in self.sounds and now - self.last_play.get(name, -1000) >= (55 if name == "type" else 90):
            self.sounds[name].play()
            self.last_play[name] = now

    def hover(self, state, point):
        target = target_at(state, point)
        key = (state, target)
        if key != self.previous and target and target != 'advance':
            self.play('hover')
        self.previous = key

    def click(self, state, point):
        target = target_at(state, point)
        if target:
            self.play(target if target in ('back', 'toggle', 'advance') else 'click')
