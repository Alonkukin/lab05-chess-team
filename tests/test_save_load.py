import json

import pytest

from game import new_position
from session import Session


def test_save_load_restores_game_and_earlier_positions(tmp_path):
    path = tmp_path / "match.save.json"
    original = Session("computer")
    original.play("e2", "e4")
    original.play("d7", "d5")
    original.play("e4", "d5")
    original.dispatch({"action": "save", "path": str(path)})

    restored = Session()
    restored.dispatch({"action": "load", "path": str(path)})
    assert restored.view() == original.view()
    assert restored.history == original.history
    assert restored.history[0] == new_position()
    assert restored.history[-1][0]["d5"] == "bP"
    assert restored.history[-1][0]["e4"] == "wP"
    assert restored.position[0]["d5"] == "wP"
    assert restored.computer_to_move()

    restored.dispatch({"action": "computer-move"})
    assert len(restored.notation) == 4
    assert len(restored.history) == 4


def test_save_load_new_game_and_missing_file(tmp_path):
    path = tmp_path / "match.save.json"
    session = Session()
    session.dispatch({"action": "move", "source": "e2", "target": "e4"})
    session.save(path)
    session.dispatch({"action": "new", "opponent": "computer"})
    assert session.history == []
    session.load(path)
    assert session.position[1] == "b"
    assert session.opponent == "human"
    assert session.notation == ["e2-e4"]
    before = session.view().copy()
    with pytest.raises(ValueError, match="Could not load save file"):
        session.load(tmp_path / "missing.json")
    assert session.view() == before


@pytest.mark.parametrize("contents", [
    "{broken",
    "[]",
    json.dumps({"version": 99, "position": new_position(), "notation": [],
                "opponent": "human", "history": []}),
    json.dumps({"version": 1, "position": [{"z9": "wK"}, "w"],
                "notation": [], "opponent": "human", "history": []}),
    json.dumps({"version": 1, "position": new_position(),
                "notation": ["e2-e4"], "opponent": "human", "history": []}),
    json.dumps({"version": 1, "position": new_position(),
                "notation": ["e2-e4"], "opponent": "human",
                "history": [[{"e2": "invalid"}, "w"]]}),
])
def test_invalid_saves_leave_session_untouched(tmp_path, contents):
    path = tmp_path / "broken.save.json"
    path.write_text(contents)
    session = Session()
    session.play("e2", "e4")
    before = (session.position[0].copy(), session.position[1],
              session.notation.copy(), session.history.copy(), session.opponent)
    with pytest.raises(ValueError, match="save file"):
        session.load(path)
    assert (session.position[0], session.position[1], session.notation,
            session.history, session.opponent) == before


def test_save_replaces_file_with_current_game(tmp_path):
    path = tmp_path / "match.save.json"
    session = Session()
    session.save(path)
    session.play("e2", "e4")
    session.save(path)
    restored = Session()
    restored.load(path)
    assert restored.view() == session.view()
