"""Tests for legal swap enumeration."""

# ruff: noqa: E402

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from game.board import BoardState
from game.gem import GemType
from game.moves import (
    enumerate_swaps,
    filter_productive_swaps,
    is_productive_swap,
    simulate_move,
)
from game.rules import find_matches


def make_supplier(sequence: list[GemType]) -> Callable[[], GemType]:
    """Return a deterministic gem supplier from a sequence."""

    iterator = iter(sequence)

    def supplier() -> GemType:
        return next(iterator)

    return supplier


def assert_no_empty_cells(board: BoardState) -> None:
    """Assert that the board contains no empty gems."""

    assert all(
        gem is not GemType.EMPTY
        for row in board.rows
        for gem in row
    )


def assert_no_matches(board: BoardState) -> None:
    """Assert that the board contains no matches."""

    assert not find_matches(board)


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
        [GemType.RED, GemType.PURPLE, GemType.GREEN],
    ]
    board = BoardState.from_rows(rows)

    swaps = [((0, 0), (1, 0))]

    assert filter_productive_swaps(board, swaps) == []


def test_filter_productive_swaps_skips_empty_cells() -> None:
    """Exclude swaps that involve empty gems."""

    rows = [
        [GemType.RED, GemType.EMPTY, GemType.RED],
        [GemType.BLUE, GemType.GREEN, GemType.BLUE],
        [GemType.YELLOW, GemType.PURPLE, GemType.GREEN],
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


def test_simulate_move_single_swap_resolves_to_expected_board() -> None:
    """Simulate a productive swap and resolve to a stable board."""

    rows = [
        [GemType.RED, GemType.BLUE, GemType.GREEN],
        [GemType.BLUE, GemType.RED, GemType.BLUE],
        [GemType.YELLOW, GemType.GREEN, GemType.PURPLE],
    ]
    board = BoardState.from_rows(rows)
    swap = ((1, 0), (1, 1))
    supplier = make_supplier([GemType.BLUE, GemType.YELLOW, GemType.PURPLE])

    result = simulate_move(board, swap, supplier)

    expected = (
        (GemType.RED, GemType.RED, GemType.GREEN),
        (GemType.YELLOW, GemType.GREEN, GemType.PURPLE),
        (GemType.BLUE, GemType.YELLOW, GemType.PURPLE),
    )
    assert result.rows == expected
    assert_no_empty_cells(result)
    assert_no_matches(result)


def test_simulate_move_multi_cascade_resolves_fully() -> None:
    """Resolve a swap that triggers multiple cascades."""

    rows = [
        [GemType.RED, GemType.RED, GemType.BLUE],
        [GemType.BLUE, GemType.GREEN, GemType.RED],
        [GemType.BLUE, GemType.GREEN, GemType.BLUE],
    ]
    board = BoardState.from_rows(rows)
    swap = ((2, 0), (2, 1))
    supplier = make_supplier([
        GemType.BLUE,
        GemType.GREEN,
        GemType.BLUE,
        GemType.RED,
        GemType.GREEN,
        GemType.BLUE,
        GemType.YELLOW,
        GemType.PURPLE,
        GemType.YELLOW,
        GemType.RED,
        GemType.BLUE,
        GemType.GREEN,
    ])

    result = simulate_move(board, swap, supplier)

    expected = (
        (GemType.BLUE, GemType.YELLOW, GemType.GREEN),
        (GemType.GREEN, GemType.PURPLE, GemType.BLUE),
        (GemType.RED, GemType.YELLOW, GemType.RED),
    )
    assert result.rows == expected
    assert_no_empty_cells(result)
    assert_no_matches(result)


def test_simulate_move_preserves_input_board() -> None:
    """Ensure simulate_move does not mutate the input board."""

    rows = [
        [GemType.RED, GemType.BLUE, GemType.GREEN],
        [GemType.BLUE, GemType.RED, GemType.BLUE],
        [GemType.YELLOW, GemType.GREEN, GemType.PURPLE],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows
    swap = ((1, 0), (1, 1))
    supplier = make_supplier([GemType.BLUE, GemType.YELLOW, GemType.PURPLE])

    simulate_move(board, swap, supplier)

    assert board.rows is original_rows


def test_simulate_move_deterministic_with_same_supplier() -> None:
    """Same supplier sequence yields identical results."""

    rows = [
        [GemType.RED, GemType.BLUE, GemType.GREEN],
        [GemType.BLUE, GemType.RED, GemType.BLUE],
        [GemType.YELLOW, GemType.GREEN, GemType.PURPLE],
    ]
    board = BoardState.from_rows(rows)
    swap = ((1, 0), (1, 1))

    first = simulate_move(
        board,
        swap,
        make_supplier([GemType.BLUE, GemType.YELLOW, GemType.PURPLE]),
    )
    second = simulate_move(
        board,
        swap,
        make_supplier([GemType.BLUE, GemType.YELLOW, GemType.PURPLE]),
    )

    assert first.rows == second.rows
    assert_no_empty_cells(first)
    assert_no_matches(first)


def test_simulate_move_varies_with_different_suppliers() -> None:
    """Different supplier sequences yield different results."""

    rows = [
        [GemType.RED, GemType.BLUE, GemType.GREEN],
        [GemType.BLUE, GemType.RED, GemType.BLUE],
        [GemType.YELLOW, GemType.GREEN, GemType.PURPLE],
    ]
    board = BoardState.from_rows(rows)
    swap = ((1, 0), (1, 1))

    first = simulate_move(
        board,
        swap,
        make_supplier([GemType.BLUE, GemType.YELLOW, GemType.PURPLE]),
    )
    second = simulate_move(
        board,
        swap,
        make_supplier([GemType.GREEN, GemType.PURPLE, GemType.YELLOW]),
    )

    assert first.rows != second.rows
    assert_no_empty_cells(first)
    assert_no_matches(first)
    assert_no_empty_cells(second)
    assert_no_matches(second)


def test_simulate_move_swap_uses_allowed_colors() -> None:
    """Swap uses playable gem colors and produces a valid board."""

    rows = [
        [GemType.RED, GemType.BLUE, GemType.GREEN],
        [GemType.BLUE, GemType.RED, GemType.BLUE],
        [GemType.YELLOW, GemType.GREEN, GemType.PURPLE],
    ]
    board = BoardState.from_rows(rows)
    swap = ((1, 0), (1, 1))
    supplier = make_supplier([GemType.BLUE, GemType.YELLOW, GemType.PURPLE])
    allowed = {
        GemType.RED,
        GemType.BLUE,
        GemType.GREEN,
        GemType.YELLOW,
        GemType.PURPLE,
    }

    assert board.get(*swap[0]) in allowed
    assert board.get(*swap[1]) in allowed

    result = simulate_move(board, swap, supplier)

    assert all(
        gem in allowed
        for row in result.rows
        for gem in row
    )
    assert_no_empty_cells(result)
    assert_no_matches(result)
