"""Application actions and information shown beside the board."""

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from computer import choose_move
from game import (
    coordinates,
    copy_position,
    legal_moves,
    move,
    new_position,
    status,
    winner,
)

DEFAULT_SAVE = Path(__file__).resolve().parent / "game.save.json"
SAVE_VERSION = 1
PIECES = {side + kind for side in "wb" for kind in "KQRBNP"}


def valid_position(value):
    if (not isinstance(value, list) or len(value) != 2
            or not isinstance(value[0], dict) or value[1] not in ("w", "b")):
        raise ValueError("Invalid save file: bad position")
    for square, piece in value[0].items():
        try:
            coordinates(square)
        except ValueError as error:
            raise ValueError("Invalid save file: bad square") from error
        if not isinstance(piece, str) or piece not in PIECES:
            raise ValueError("Invalid save file: bad piece")
    return copy_position(value)


def parse_save(data):
    if not isinstance(data, dict) or set(data) != {
            "version", "position", "notation", "opponent", "history"}:
        raise ValueError("Invalid save file: unexpected fields")
    if type(data["version"]) is not int or data["version"] != SAVE_VERSION:
        raise ValueError("Invalid save file: unsupported version")
    if data["opponent"] not in ("human", "computer"):
        raise ValueError("Invalid save file: bad opponent")
    notation = data["notation"]
    history = data["history"]
    if (not isinstance(notation, list) or not isinstance(history, list)
            or len(notation) != len(history)
            or any(not isinstance(label, str) or not label for label in notation)):
        raise ValueError("Invalid save file: bad move history")
    position = valid_position(data["position"])
    snapshots = [valid_position(item) for item in history]
    return position, notation.copy(), data["opponent"], snapshots


# Legal from the standard starting position under this game's rules.
# Next move: b7-a8, capturing a rook and reaching the last rank.
PROMOTION_SETUP = [
    ("a2", "a4"), ("h7", "h5"),
    ("a4", "a5"), ("h5", "h4"),
    ("a5", "a6"), ("h4", "h3"),
    ("a6", "b7"), ("h3", "g2"),
]


class Session:
    def __init__(self, opponent="human"):
        if opponent not in ("human", "computer"):
            raise ValueError("Unknown opponent")
        self.position = new_position()
        self.notation = []
        self.history = []
        self.opponent = opponent

    def play(self, source, target):
        before = copy_position(self.position)
        label = move(self.position, source, target)
        self.history.append(before)
        self.notation.append(label)
        self.after_move()

    def save(self, path=DEFAULT_SAVE):
        data = {"version": SAVE_VERSION, "position": self.position,
                "notation": self.notation, "opponent": self.opponent,
                "history": self.history}
        path = Path(path)
        temporary = None
        try:
            with NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                    prefix=".chess-save-", delete=False) as file:
                temporary = Path(file.name)
                json.dump(data, file)
                file.write("\n")
            os.replace(temporary, path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def load(self, path=DEFAULT_SAVE):
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ValueError(f"Could not load save file: {error}") from error
        position, notation, opponent, history = parse_save(data)
        self.position = position
        self.notation = notation
        self.opponent = opponent
        self.history = history

    def after_move(self):
        pass

    def view(self):
        return {
            "board": self.position[0],
            "turn": self.position[1],
            "moves": self.notation,
            "opponent": self.opponent,
            "status": status(self.position),
            "winner": winner(self.position),
            **self.sidebar(),
        }

    def computer_to_move(self):
        return (self.opponent == "computer" and self.position[1] == "b"
                and status(self.position) not in ("checkmate", "stalemate"))

    def sidebar(self):
        return {}

    def dispatch(self, action):
        command = action.get("action")
        if command == "move":
            if self.computer_to_move():
                raise ValueError("Wait for the computer's move")
            self.play(action.get("source"), action.get("target"))
        elif command == "computer-move":
            if not self.computer_to_move():
                raise ValueError("It is not the computer's turn")
            self.play(*choose_move(self.position))
        elif command == "legal":
            return {"targets": legal_moves(self.position, action.get("source"))}
        elif command == "new":
            self.__init__(action.get("opponent", "human"))
        elif command == "promotion-setup":
            self.__init__()
            for source, target in PROMOTION_SETUP:
                self.play(source, target)
        elif command == "save":
            self.save(action.get("path", DEFAULT_SAVE))
        elif command == "load":
            self.load(action.get("path", DEFAULT_SAVE))
        else:
            raise ValueError("Unknown action")
        return self.view()
