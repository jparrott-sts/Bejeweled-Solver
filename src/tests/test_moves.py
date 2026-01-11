"""Tests for legal swap enumeration."""

# ruff: noqa: E402

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from game.board import BoardState
from game.gem import GemType
from game.moves import enumerate_swaps


def test_enumerate_swaps_ordering_and_immutability() -> None:
    """Enumerate swaps in stable order without mutating the board."""

    rows = [
        [GemType.RED, GemType.BLUE],
        [GemType.GREEN, GemType.YELLOW],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows

    swaps = enumerate_swaps(board)

    assert swaps == [
        ((0, 0), (1, 0)),
        ((0, 0), (0, 1)),
        ((1, 0), (1, 1)),
        ((0, 1), (1, 1)),
    ]
    assert len(swaps) == len(set(swaps))
    assert board.rows is original_rows


def test_enumerate_swaps_excludes_empty_cells() -> None:
    """Exclude swaps that involve empty gems."""

    rows = [
        [GemType.RED, GemType.EMPTY],
        [GemType.GREEN, GemType.BLUE],
    ]
    board = BoardState.from_rows(rows)

    swaps = enumerate_swaps(board)

    assert swaps == [
        ((0, 0), (0, 1)),
        ((0, 1), (1, 1)),
    ]


def test_enumerate_swaps_handles_edges_and_corners() -> None:
    """Handle edge coordinates without out-of-bounds swaps."""

    rows = [
        [GemType.RED],
        [GemType.BLUE],
        [GemType.GREEN],
    ]
    board = BoardState.from_rows(rows)

    swaps = enumerate_swaps(board)

    assert swaps == [
        ((0, 0), (0, 1)),
        ((0, 1), (0, 2)),
    ]
