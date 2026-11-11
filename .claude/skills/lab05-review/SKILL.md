---
name: lab05-review
description: Quick end-of-lab review of a pair's chess game from Lab 5 of the AICODE course (testing, linting, formatting and type checking with a coding agent). Runs the project's checks, skims the code, tests and Git history, and writes lab05-review.md for the pair to compare with their own view and upload. Use when the pair asks for the Lab 5 review.
allowed-tools: Read, Grep, Glob, Write, Read(~/.claude/projects/**), Read(~/.codex/sessions/**), Bash(python -m pytest:*), Bash(python3 -m pytest:*), Bash(pytest:*), Bash(.venv/bin/python -m pytest:*), Bash(.venv/bin/pytest:*), Bash(ruff:*), Bash(.venv/bin/ruff:*), Bash(mypy:*), Bash(.venv/bin/mypy:*), Bash(git log:*), Bash(git show:*), Bash(git diff:*), Bash(git branch:*), Bash(git rev-parse:*), Bash(git status:*), Bash(grep:*), Bash(wc:*), Bash(ls:*), Bash(head:*), Bash(tail:*)
---

# Lab 5 review

## The context

This repository is a pair's work from a 90-minute lab in AICODE, a university course on
programming with coding agents. The handout is at https://aicode-huji.pages.dev/week/5/lab/;
you do not need to read it. The pair started from a small Python chess game (a local server in
`server.py`, game logic in Python, a browser interface in `static/`, pytest tests in `tests/`)
and, with their agents:

- added save and load, and undo, on two separate branches, then merged them;
- merged two supplied branches, captured pieces and promotion, and fixed what broke;
- ran Ruff, mypy and a coverage report;
- added redo together, then features of their own if time allowed.

The week taught them to check an agent's work with tests (one per feature, and tests of features
that share state), a linter and a formatter (Ruff), a type checker (`mypy --strict`), and an
instruction file that names these checks.

## The job

Write a **quick** review in `lab05-review.md` in the repository root. The pair is in a class
discussion while you work, then compares your review with what they said and uploads it. Aim to
finish in about five minutes.

- **Evidence, not coverage.** For each item, cite the first good evidence you find: a
  `file:line`, a commit hash, or a command's output. If an item would take long to settle, write
  "not checked" and move on.
- **Change nothing.** Don't edit code, tests, configuration or history, don't install anything,
  don't commit, and don't start the server. The only file you write is `lab05-review.md`.
  Files the checks write themselves (`.coverage`, `.pytest_cache`, `.mypy_cache`,
  `.ruff_cache`) are fine: run the checks as they are.
- **Don't ask the pair anything.** They are away. Where you cannot tell, write "unknown".
- **Name what was done well**, with the same kind of evidence.
- **About 500 words.** Plain sentences, no hedging.

## 1. Run the checks, once each

Run each command on its own, through `.venv/bin/` when there is a `.venv`: no `source`, `;`,
`&&` or shell variables, so that none of them stops to ask the pair for permission. A tool that is
not installed is "not set up"; don't install it.

- `.venv/bin/python -m pytest -q --durations=3`, with `--cov=. --cov-report=term` if `pytest-cov`
  is installed
- `.venv/bin/ruff check .` and `.venv/bin/ruff format --check .`
- `.venv/bin/mypy --strict .`

Then read the history once: `git log --oneline --stat --all`, and `git branch -a --no-merged main`.

## 2. The week's practices

Mark each ✅ (done), ⚠️ (partly), ❌ (missing) or "not checked", with one line of evidence.

1. **Tests for each feature:** save and load, undo, redo, captured pieces, promotion, and the
   pair's own features. Name a feature with no tests.
2. **Tests of features together**, where they share state: for example undo after a capture or
   a promotion, or a loaded game keeping its undo history.
3. **Assertions that check results:** no prints in place of asserts, no test that only runs the
   code. Spot-check a few tests.
4. **Fast and repeatable:** the run time, and whether the computer opponent is seeded or replaced
   in tests.
5. **Bugs became tests:** do the fix commits in the history touch `tests/`?
6. **No weakened tests:** `git log -p -- tests/ | grep -E '^-\s*assert'`; say whether a removed
   assertion was replaced.
7. **Coverage:** the total and the least covered file, or "not set up".
8. **Linted beyond the defaults:** Ruff selects more than its default rules in `pyproject.toml`;
   the number of findings and of `# noqa`.
9. **Formatted:** `ruff format --check` passes.
10. **Type-checked:** the number of `mypy --strict` errors, and of `Any` and `# type: ignore`.
11. **From the start or at the end:** in the history, did the tool configuration and annotations
    arrive early, or in one cleanup near the end?
12. **Checks in the instruction file:** `CLAUDE.md` or `AGENTS.md` names the exact check
    commands; say whether a hook in `.claude/settings.json` runs them.

## 3. The game state

Find where the game's state is defined: the board, the side to move, and what the features added
(move notation, captured pieces, undo and redo history, opponent mode).

- **Its shape:** a class or dataclass with named fields, a dictionary, or a list or tuple read by
  position (`position[0]`). For a list or tuple, count its items now and in the starter commit.
- **Where the rest lives:** which of that information sits outside it (on the session, in the
  browser), and whether the function that copies the state, and the code that saves it, include
  every part. Read those functions only.
- **Whether it was restructured during the lab:** `git log --oneline -- game.py session.py` and
  the commit where it became a different kind of structure (a list became a class, for example),
  if any. Items added to the same list are growth, not a restructuring. For who started a
  restructuring, read the commit message and search once for the commit's main new name in this
  laptop's agent logs (Claude Code: `~/.claude/projects/`, Codex: `~/.codex/sessions/`), with
  your file-search tool rather than a shell command (in Claude Code, Grep in files-with-matches
  mode), so no permission prompt stops the review. If a log turns up, read the student message
  before the change: did a student ask for it, or did the agent propose it? Otherwise write
  "unknown". Quote no more than a short phrase from a log.

## 4. Other findings

Up to three, the most serious first, from what you have already read: how save and load treat
the file (a path from the browser, `pickle`, a malformed save), behaviour a player would notice,
or code structure.

## The report

Write `lab05-review.md` in this shape. In the two game-state rows, use exactly the words offered,
so that the class's reviews can be counted.

```markdown
# Lab 5 review

Commit reviewed: <short hash on main> · Reviewer: <agent and model> · Unmerged branches: <names or none>

## Highlights

- <three to five bullets, the most important first: what to fix first and what was done well;
  one of them is about the game state>

## At a glance

| Check | Result |
| --- | --- |
| Tests | <N passed, N failed, in N s> |
| Coverage | <N% total; lowest: file N%> or not set up |
| `ruff check` | <N findings> or not set up |
| `ruff format --check` | <N files would change> or not set up |
| `mypy --strict` | <N errors in N files> or not set up |
| Game state | list or tuple of <N> items (<N> in the starter) / dictionary / class or dataclass |
| Game state restructured in the lab | no / yes (<hash>), asked for by a student / yes (<hash>), proposed by an agent / yes (<hash>), unknown |
| Instruction file | <file and the commands it names> or none |

## The week's practices

<items 1 to 12, numbered: ✅, ⚠️, ❌ or not checked, the item's name, one line of evidence>

## The game state

<one short paragraph>

## Other findings

<up to three bullets>
```

When the file is written, say so in one line.
