import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
from best_served_warm import storage
from best_served_warm.app import App


def test_menu_buttons_save_load_and_options(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "data_dir", lambda: tmp_path)
    app = App()
    try:
        assert app.music.energies is None
        assert not hasattr(app, "visualizer")
        assert all(len(button.frames) == 5 for button in app.buttons.values())
        assert len(app.cursor.frames) == 5
        assert 30 <= app.cursor.frames[0].get_width() <= 45
        app.window = pygame.display.set_mode((960, 540), pygame.RESIZABLE)
        assert app.pointer((480, 540 * 318 / 720)) == (640, 318)
        app.window = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        app.draw()
        app.click(app.buttons["new"].rect.center)
        assert app.state == "game"
        app.click((640,545))
        assert app.game["score"] == 10
        app.click((170,76))
        app.click(app.buttons["load"].rect.center)
        assert app.state == "game" and app.game["score"] == 10
        app.click((170,76))
        app.click(app.buttons["options"].rect.center)
        assert app.state == "options"
        app.click((640,310))
        assert app.options["volume"] == 0.5
        app.click((640,612))
        assert storage.load_options()["volume"] == 0.5
        app.click(app.buttons["exit"].rect.center)
        assert app.running is False
    finally:
        app.music.close()
        pygame.quit()
