"""Tests for legal swap enumeration."""

# ruff: noqa: E402

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from game.board import BoardState
from game.gem import GemType
from game.moves import enumerate_swaps, filter_productive_swaps, is_productive_swap


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


def test_is_productive_swap_detects_horizontal_match() -> None:
    """Identify swaps that create a horizontal match."""

    rows = [
        [GemType.RED, GemType.BLUE, GemType.RED],
        [GemType.GREEN, GemType.RED, GemType.BLUE],
        [GemType.YELLOW, GemType.GREEN, GemType.BLUE],
    ]
    board = BoardState.from_rows(rows)

    swap = ((1, 0), (1, 1))

    assert is_productive_swap(board, swap) is True


def test_is_productive_swap_detects_vertical_match() -> None:
    """Identify swaps that create a vertical match."""

    rows = [
        [GemType.RED, GemType.BLUE, GemType.GREEN],
        [GemType.GREEN, GemType.RED, GemType.BLUE],
        [GemType.RED, GemType.YELLOW, GemType.PURPLE],
    ]
    board = BoardState.from_rows(rows)

    swap = ((0, 1), (1, 1))

    assert is_productive_swap(board, swap) is True


def test_filter_productive_swaps_detects_multiple_matches() -> None:
    """Keep swaps that create multiple matches."""

    rows = [
        [GemType.BLUE, GemType.RED, GemType.BLUE],
        [GemType.RED, GemType.BLUE, GemType.RED],
        [GemType.GREEN, GemType.RED, GemType.GREEN],
    ]
    board = BoardState.from_rows(rows)

    swaps = [((1, 0), (1, 1))]

    assert filter_productive_swaps(board, swaps) == [((1, 0), (1, 1))]


def test_filter_productive_swaps_excludes_non_matches() -> None:
    """Drop swaps that do not create matches."""

    rows = [
        [GemType.RED, GemType.BLUE, GemType.GREEN],
        [GemType.GREEN, GemType.YELLOW, GemType.BLUE],
        [GemType.RED, GemType.PURPLE, GemType.ORANGE],
    ]
    board = BoardState.from_rows(rows)

    swaps = [((0, 0), (1, 0))]

    assert filter_productive_swaps(board, swaps) == []


def test_filter_productive_swaps_skips_empty_cells() -> None:
    """Exclude swaps that involve empty gems."""

    rows = [
        [GemType.RED, GemType.EMPTY, GemType.RED],
        [GemType.BLUE, GemType.GREEN, GemType.BLUE],
        [GemType.YELLOW, GemType.PURPLE, GemType.ORANGE],
    ]
    board = BoardState.from_rows(rows)

    swaps = [((0, 0), (1, 0))]

    assert filter_productive_swaps(board, swaps) == []


def test_filter_productive_swaps_preserves_board() -> None:
    """Ensure productive swap filtering does not mutate the board."""

    rows = [
        [GemType.RED, GemType.BLUE, GemType.RED],
        [GemType.GREEN, GemType.RED, GemType.BLUE],
        [GemType.YELLOW, GemType.GREEN, GemType.BLUE],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows

    swaps = [((1, 0), (1, 1))]

    filter_productive_swaps(board, swaps)

    assert board.rows is original_rows
