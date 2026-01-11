"""Tests for match detection rules."""

# ruff: noqa: E402

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from game.board import BoardState
from game.gem import GemType
from game.rules import find_matches, remove_matches


def test_horizontal_match_detection() -> None:
    """Detect horizontal matches of three or more gems."""

    rows = [
        [GemType.RED, GemType.RED, GemType.RED, GemType.BLUE],
        [GemType.GREEN, GemType.YELLOW, GemType.BLUE, GemType.YELLOW],
        [GemType.YELLOW, GemType.PURPLE, GemType.GREEN, GemType.BLUE],
    ]
    board = BoardState.from_rows(rows)

    matches = find_matches(board)

    assert matches == {(0, 0), (1, 0), (2, 0)}


def test_vertical_match_detection() -> None:
    """Detect vertical matches of three or more gems."""

    rows = [
        [GemType.GREEN, GemType.RED, GemType.BLUE],
        [GemType.GREEN, GemType.YELLOW, GemType.BLUE],
        [GemType.GREEN, GemType.BLUE, GemType.PURPLE],
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


def test_empty_cells_do_not_match() -> None:
    """Ensure empty cells are not considered matchable gems."""

    rows = [
        [GemType.EMPTY, GemType.EMPTY, GemType.EMPTY],
        [GemType.RED, GemType.GREEN, GemType.BLUE],
        [GemType.YELLOW, GemType.PURPLE, GemType.BLUE],
    ]
    board = BoardState.from_rows(rows)

    matches = find_matches(board)

    assert matches == set()


def test_remove_horizontal_match() -> None:
    """Remove a horizontal match by clearing matched coordinates."""

    rows = [
        [GemType.RED, GemType.RED, GemType.RED, GemType.BLUE],
        [GemType.GREEN, GemType.YELLOW, GemType.BLUE, GemType.YELLOW],
    ]
    board = BoardState.from_rows(rows)
    matches = {(0, 0), (1, 0), (2, 0)}

    updated = remove_matches(board, matches)

    assert updated.rows == (
        (GemType.EMPTY, GemType.EMPTY, GemType.EMPTY, GemType.BLUE),
        (GemType.GREEN, GemType.YELLOW, GemType.BLUE, GemType.YELLOW),
    )
    assert board.get(0, 0) is GemType.RED


def test_remove_vertical_match() -> None:
    """Remove a vertical match by clearing matched coordinates."""

    rows = [
        [GemType.GREEN, GemType.RED],
        [GemType.GREEN, GemType.YELLOW],
        [GemType.GREEN, GemType.BLUE],
    ]
    board = BoardState.from_rows(rows)
    matches = {(0, 0), (0, 1), (0, 2)}

    updated = remove_matches(board, matches)

    assert updated.rows == (
        (GemType.EMPTY, GemType.RED),
        (GemType.EMPTY, GemType.YELLOW),
        (GemType.EMPTY, GemType.BLUE),
    )
    assert board.get(0, 1) is GemType.GREEN


def test_remove_overlapping_matches() -> None:
    """Remove overlapping T-shape matches without duplication issues."""

    rows = [
        [GemType.RED, GemType.GREEN, GemType.RED],
        [GemType.GREEN, GemType.GREEN, GemType.GREEN],
        [GemType.RED, GemType.GREEN, GemType.RED],
    ]
    board = BoardState.from_rows(rows)
    matches = {(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)}

    updated = remove_matches(board, matches)

    assert updated.rows == (
        (GemType.RED, GemType.EMPTY, GemType.RED),
        (GemType.EMPTY, GemType.EMPTY, GemType.EMPTY),
        (GemType.RED, GemType.EMPTY, GemType.RED),
    )
    assert board.get(1, 1) is GemType.GREEN


def test_remove_empty_match_set_returns_same_board() -> None:
    """Return identical board when no matches are provided."""

    rows = [
        [GemType.BLUE, GemType.RED],
        [GemType.YELLOW, GemType.GREEN],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows

    updated = remove_matches(board, set())

    assert updated.rows == original_rows
    assert board.rows == original_rows
