import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import numpy as np
import pygame
from best_served_warm import storage
from best_served_warm.app import App


def test_menu_save_load_options_and_audio_bar(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "data_dir", lambda: tmp_path)
    app = App()
    try:
        assert len(app.music.energies) > 100
        assert app.music.energies.shape[1] == 28
        assert np.max(app.music.energies) > 0.1
        app.visualizer.update(np.ones(28, dtype=np.float32), 0.1)
        assert 0 < app.visualizer.smoothed[0] < 1
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
        app.click((640,405))
        assert not app.options["visualizer"]
        app.click((640,612))
        assert storage.load_options()["visualizer"] is False
    finally:
        app.music.close()
        pygame.quit()
