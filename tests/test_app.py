import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from best_served_warm import storage
from best_served_warm.app import App


def test_pause_save_and_load_story(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "data_dir", lambda: tmp_path)
    app = App()
    try:
        app.click((96, 65))
        assert app.state == "loading"
        app.state = "dialogue"
        app.dialogue.page = 1
        app.dialogue.revealed = 27.0
        app.paused_from = "dialogue"
        app.state = "pause"
        app.draw()
        app.click((96, 67))
        assert storage.load_game()["page"] == 1
        assert storage.load_game()["revealed"] == 27.0
        app.click((96, 83))
        assert app.state == "menu"
        app.click((96, 77))
        assert app.state == "dialogue"
        assert app.dialogue.page == 1
        assert app.dialogue.revealed == 27.0
        app.draw()
    finally:
        app.music.close()
        pygame.quit()


def test_station_entry_and_pause(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, 'data_dir', lambda: tmp_path)
    app = App()
    try:
        app.state = 'customer'
        app.click((140, 92))
        assert app.customer_step == 1
        app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        assert app.state == 'loading' and app.loading_target == 'cup_station'
        app.state = 'cup_station'
        app.scene_fade = 1.0
        app.click((159,52))  # Medium ceramic mug on the supplied rack.
        app.click((96,73))   # Place it on the counter.
        assert app.coffee_station.placed[-1]['size'] == 'M'
        app.click((96,100))  # Continue to the next station.
        assert app.state == 'coffee'
        assert app.kitchen.cups['cup_1'].style == 'mug'
        assert app.kitchen.cups['cup_1'].size == 'M'
        app.draw()
        assert app.kitchen.cups['cup_1'].location == 'espresso'
        app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        assert app.state == 'pause'
        app.draw()
        app.click((96,67))
        app.click((96,83))
        app.click((96,77))
        assert app.state == 'coffee'
        assert app.kitchen.cups['cup_1'].location == 'espresso'
        assert app.kitchen.cups['cup_1'].size == 'M'
    finally:
        app.music.close()
        pygame.quit()


def test_customer_and_cup_station_resume(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, 'data_dir', lambda: tmp_path)
    app = App()
    try:
        app.state = 'customer'
        app.click((140, 92))
        app.paused_from = 'customer'
        app.state = 'pause'
        app.click((96, 67))
        assert app.load_progress()
        assert (app.state, app.customer_step) == ('customer', 1)

        app.start_cup_station()
        app.state = 'cup_station'
        app.scene_fade = 1.0
        app.click((159, 52))
        app.click((96, 73))
        app.paused_from = 'cup_station'
        app.state = 'pause'
        app.click((96, 67))
        assert app.load_progress()
        assert app.state == 'cup_station'
        assert len(app.coffee_station.placed) == 1
        assert app.coffee_station.placed[0]['style'] == 'mug'
    finally:
        app.music.close()
        pygame.quit()
