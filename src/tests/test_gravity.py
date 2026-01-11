"""Tests for inverted gravity resolution."""

# ruff: noqa: E402

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from game.board import BoardState
from game.gem import GemType
from game.gravity import apply_gravity


def test_single_gap_in_column() -> None:
    """Gems rise into a single empty space in their column."""

    rows = [
        [GemType.EMPTY],
        [GemType.RED],
        [GemType.BLUE],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows

    updated = apply_gravity(board)

    expected = (
        (GemType.RED,),
        (GemType.BLUE,),
        (GemType.EMPTY,),
    )
    assert updated.rows == expected
    assert board.rows == original_rows


def test_multiple_gaps_in_column() -> None:
    """Multiple empty spaces are filled upward while preserving order."""

    rows = [
        [GemType.EMPTY],
        [GemType.GREEN],
        [GemType.EMPTY],
        [GemType.RED],
        [GemType.EMPTY],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows

    updated = apply_gravity(board)

    expected = (
        (GemType.GREEN,),
        (GemType.RED,),
        (GemType.EMPTY,),
        (GemType.EMPTY,),
        (GemType.EMPTY,),
    )
    assert updated.rows == expected
    assert board.rows == original_rows


def test_entire_column_empty() -> None:
    """A fully empty column remains unchanged."""

    rows = [
        [GemType.EMPTY],
        [GemType.EMPTY],
        [GemType.EMPTY],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows

    updated = apply_gravity(board)

    expected = (
        (GemType.EMPTY,),
        (GemType.EMPTY,),
        (GemType.EMPTY,),
    )
    assert updated.rows == expected
    assert board.rows == original_rows


def test_mixed_columns_with_unaffected_column() -> None:
    """Columns resolve independently and stable columns remain unchanged."""

    rows = [
        [GemType.EMPTY, GemType.RED],
        [GemType.BLUE, GemType.GREEN],
        [GemType.EMPTY, GemType.YELLOW],
        [GemType.PURPLE, GemType.BLUE],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows

    updated = apply_gravity(board)

    expected = (
        (GemType.BLUE, GemType.RED),
        (GemType.PURPLE, GemType.GREEN),
        (GemType.EMPTY, GemType.YELLOW),
        (GemType.EMPTY, GemType.BLUE),
    )
    assert updated.rows == expected
    assert board.rows == original_rows


def test_already_stable_board_returns_identical() -> None:
    """Boards with no empty spaces above gems remain unchanged."""

    rows = [
        [GemType.RED, GemType.BLUE],
        [GemType.GREEN, GemType.YELLOW],
        [GemType.EMPTY, GemType.EMPTY],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows

    updated = apply_gravity(board)

    expected = (
        (GemType.RED, GemType.BLUE),
        (GemType.GREEN, GemType.YELLOW),
        (GemType.EMPTY, GemType.EMPTY),
    )
    assert updated.rows == expected
    assert updated == board
    assert board.rows == original_rows
