import json
from best_served_warm import storage


def test_save_roundtrip_and_bad_save(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "data_dir", lambda: tmp_path)
    game = storage.new_game()
    game["score"] = 30
    game["served"] = 3
    storage.save_game(game)
    assert storage.load_game() == game
    (tmp_path / "save.json").write_text('{"score":"broken"}')
    assert storage.load_game() is None


def test_option_bounds(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "data_dir", lambda: tmp_path)
    (tmp_path / "options.json").write_text(json.dumps({"volume": 3, "visualizer": False}))
    assert storage.load_options()["volume"] == 1
    assert storage.load_options()["visualizer"] is False
