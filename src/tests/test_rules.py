"""Tests for match detection rules."""

# ruff: noqa: E402

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from game.board import BoardState
from game.gem import GemType
from game.rules import find_matches


def test_horizontal_match_detection() -> None:
    """Detect horizontal matches of three or more gems."""

    rows = [
        [GemType.RED, GemType.RED, GemType.RED, GemType.BLUE],
        [GemType.GREEN, GemType.YELLOW, GemType.BLUE, GemType.YELLOW],
        [GemType.ORANGE, GemType.PURPLE, GemType.GREEN, GemType.BLUE],
    ]
    board = BoardState.from_rows(rows)

    matches = find_matches(board)

    assert matches == {(0, 0), (1, 0), (2, 0)}


def test_vertical_match_detection() -> None:
    """Detect vertical matches of three or more gems."""

    rows = [
        [GemType.GREEN, GemType.RED, GemType.BLUE],
        [GemType.GREEN, GemType.YELLOW, GemType.BLUE],
        [GemType.GREEN, GemType.ORANGE, GemType.PURPLE],
    ]
    board = BoardState.from_rows(rows)

    matches = find_matches(board)

    assert matches == {(0, 0), (0, 1), (0, 2)}


def test_overlapping_t_shape_match_detection() -> None:
    """Detect overlapping matches without duplication."""

    rows = [
        [GemType.RED, GemType.GREEN, GemType.RED],
        [GemType.GREEN, GemType.GREEN, GemType.GREEN],
        [GemType.RED, GemType.GREEN, GemType.RED],
    ]
    board = BoardState.from_rows(rows)

    matches = find_matches(board)

    assert matches == {(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)}
