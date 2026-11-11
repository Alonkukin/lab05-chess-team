from copy import deepcopy

import pytest

from session import Session


def play(session, source, target):
    return session.dispatch({"action": "move", "source": source, "target": target})


def undo(session):
    return session.dispatch({"action": "undo"})


def test_undo_at_start_is_safe():
    session = Session()
    initial = deepcopy(session.view())
    assert initial["can_undo"] is False
    assert undo(session) == initial
    assert undo(session) == initial


def test_undo_restores_capture_turn_notation_and_continuation():
    session = Session()
    play(session, "e2", "e4")
    play(session, "d7", "d5")
    before_capture = deepcopy(session.view())
    play(session, "e4", "d5")
    assert session.view()["board"]["d5"] == "wP"
    assert undo(session) == before_capture
    assert session.view()["board"]["d5"] == "bP"
    assert session.view()["board"]["e4"] == "wP"
    assert play(session, "g1", "f3")["moves"] == ["e2-e4", "d7-d5", "g1-f3"]


def test_undo_after_game_ends_restores_status_and_winner():
    session = Session()
    session.position = [{"g1": "wK", "a1": "wR", "g8": "bK",
                         "f7": "bP", "g7": "bP", "h7": "bP"}, "w"]
    before = deepcopy(session.view())
    finished = play(session, "a1", "a8")
    assert finished["status"] == "checkmate"
    assert finished["winner"] == "White"
    assert undo(session) == {**before, "can_undo": False}


def test_invalid_move_does_not_create_undo_history():
    session = Session()
    with pytest.raises(ValueError):
        play(session, "e2", "e5")
    assert session.view()["can_undo"] is False
    assert undo(session)["moves"] == []


def test_computer_undo_after_reply_restores_both_moves():
    session = Session("computer")
    initial = deepcopy(session.view())
    play(session, "e2", "e4")
    session.dispatch({"action": "computer-move"})
    assert len(session.view()["moves"]) == 2
    assert undo(session) == initial


def test_computer_undo_latest_completed_turn_only():
    session = Session("computer")
    play(session, "e2", "e4")
    session.dispatch({"action": "computer-move"})
    after_first_turn = deepcopy(session.view())
    play(session, "g1", "f3")
    session.dispatch({"action": "computer-move"})
    assert len(session.view()["moves"]) == 4
    assert undo(session) == after_first_turn


def test_computer_undo_pending_reply_and_previous_turn():
    session = Session("computer")
    play(session, "e2", "e4")
    pending = deepcopy(session.view())
    assert undo(session)["moves"] == []
    play(session, "e2", "e4")
    session.dispatch({"action": "computer-move"})
    before_second_turn = deepcopy(session.view())
    assert before_second_turn["turn"] == "w"
    play(session, "g1", "f3")
    assert undo(session) == before_second_turn
    assert undo(session)["moves"] == []


def test_new_game_and_setup_replace_undo_history():
    session = Session()
    play(session, "e2", "e4")
    assert session.dispatch({"action": "new"})["can_undo"] is False
    assert undo(session)["moves"] == []
    session.dispatch({"action": "promotion-setup"})
    assert len(session.view()["moves"]) == 8
    assert len(undo(session)["moves"]) == 7
