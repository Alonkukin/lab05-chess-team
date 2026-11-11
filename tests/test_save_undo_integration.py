"""Save/load and undo must share the same position history."""

from copy import deepcopy

import pytest

from session import Session


def play(session, source, target):
    return session.dispatch({"action": "move", "source": source, "target": target})


def computer_reply(session):
    return session.dispatch({"action": "computer-move"})


@pytest.mark.parametrize("opponent", ["human", "computer"])
def test_save_load_after_undo_preserves_board_turn_and_moves(tmp_path, opponent):
    path = tmp_path / "game.json"
    game = Session(opponent)
    play(game, "e2", "e4")
    if opponent == "computer":
        computer_reply(game)
    else:
        play(game, "d7", "d5")
    expected = deepcopy(game.view())
    expected_history = deepcopy(game.history)

    play(game, "g1", "f3")
    if opponent == "computer":
        computer_reply(game)
    else:
        play(game, "g8", "f6")
        game.dispatch({"action": "undo"})
    assert game.dispatch({"action": "undo"}) == expected
    assert game.history == expected_history

    game.dispatch({"action": "save", "path": str(path)})
    restored = Session()
    assert restored.dispatch({"action": "load", "path": str(path)}) == expected
    assert restored.history == expected_history
    assert restored.opponent == opponent

    # The saved history still supports undo and a different continuation.
    restored.dispatch({"action": "undo"})
    assert len(restored.history) == len(restored.notation)
    source, target = ("d2", "d4") if opponent == "computer" else ("e7", "e5")
    assert play(restored, source, target)["moves"][-1] == f"{source}-{target}"


@pytest.mark.parametrize("opponent", ["human", "computer"])
def test_undo_after_load_restores_saved_prior_position(tmp_path, opponent):
    path = tmp_path / "game.json"
    game = Session(opponent)
    play(game, "e2", "e4")
    if opponent == "computer":
        computer_reply(game)
    before = deepcopy(game.view())
    if opponent == "computer":
        play(game, "g1", "f3")
    else:
        play(game, "e7", "e5")
    if opponent == "computer":
        computer_reply(game)
    saved = deepcopy(game.view())
    game.dispatch({"action": "save", "path": str(path)})

    loaded = Session("human" if opponent == "computer" else "computer")
    assert loaded.dispatch({"action": "load", "path": str(path)}) == saved
    assert loaded.dispatch({"action": "undo"}) == before
    assert loaded.position == before_position(game, opponent)
    assert len(loaded.history) == len(loaded.notation)


def before_position(game, opponent):
    return game.history[-2] if opponent == "computer" else game.history[-1]


def test_loaded_computer_game_with_pending_reply_can_reply_and_undo(tmp_path):
    path = tmp_path / "game.json"
    game = Session("computer")
    initial = deepcopy(game.view())
    play(game, "e2", "e4")
    game.save(path)

    loaded = Session()
    loaded.load(path)
    assert loaded.position[1] == "b"
    assert loaded.computer_to_move()
    computer_reply(loaded)
    assert len(loaded.notation) == len(loaded.history) == 2
    assert loaded.dispatch({"action": "undo"}) == initial
