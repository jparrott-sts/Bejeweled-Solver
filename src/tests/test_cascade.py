"""Tests for cascade resolution."""

# ruff: noqa: E402

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from game.board import BoardState
from game.cascade import resolve_cascades
from game.gem import GemType
from game.rules import find_matches


def make_supplier(
    sequence: list[GemType],
) -> tuple[Callable[[], GemType], dict[str, int]]:
    """Return an iterator and a call counter for deterministic supply."""

    iterator = iter(sequence)
    call_count = {"count": 0}

    def supplier() -> GemType:
        call_count["count"] += 1
        return next(iterator)

    return supplier, call_count


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


def test_no_initial_matches_returns_identical_board() -> None:
    """Boards without matches should return unchanged."""

    rows = [
        [GemType.RED, GemType.BLUE, GemType.GREEN],
        [GemType.YELLOW, GemType.PURPLE, GemType.ORANGE],
        [GemType.BLUE, GemType.GREEN, GemType.YELLOW],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows
    supplier, call_count = make_supplier([])

    resolved = resolve_cascades(board, supplier)

    assert resolved == board
    assert resolved.rows == original_rows
    assert call_count["count"] == 0
    assert board.rows == original_rows


def test_single_cascade_resolves_correctly() -> None:
    """Single cascade resolves matches and refills once."""

    rows = [
        [GemType.RED, GemType.RED, GemType.RED],
        [GemType.BLUE, GemType.GREEN, GemType.YELLOW],
        [GemType.PURPLE, GemType.ORANGE, GemType.BLUE],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows
    supplier, call_count = make_supplier([
        GemType.RED,
        GemType.GREEN,
        GemType.PURPLE,
    ])

    resolved = resolve_cascades(board, supplier)

    expected = (
        (GemType.BLUE, GemType.GREEN, GemType.YELLOW),
        (GemType.PURPLE, GemType.ORANGE, GemType.BLUE),
        (GemType.RED, GemType.GREEN, GemType.PURPLE),
    )
    assert resolved.rows == expected
    assert call_count["count"] == 3
    assert board.rows == original_rows
    assert_no_empty_cells(resolved)
    assert_no_matches(resolved)


def test_multi_cascade_chain_resolves_fully() -> None:
    """Multiple cascades resolve until stable."""

    rows = [
        [GemType.RED, GemType.RED, GemType.RED],
        [GemType.BLUE, GemType.GREEN, GemType.BLUE],
        [GemType.BLUE, GemType.GREEN, GemType.BLUE],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows
    supplier, call_count = make_supplier([
        GemType.BLUE,
        GemType.GREEN,
        GemType.BLUE,
        GemType.RED,
        GemType.GREEN,
        GemType.BLUE,
        GemType.YELLOW,
        GemType.PURPLE,
        GemType.ORANGE,
        GemType.RED,
        GemType.BLUE,
        GemType.GREEN,
    ])

    resolved = resolve_cascades(board, supplier)

    expected = (
        (GemType.BLUE, GemType.ORANGE, GemType.GREEN),
        (GemType.GREEN, GemType.PURPLE, GemType.BLUE),
        (GemType.RED, GemType.YELLOW, GemType.RED),
    )
    assert resolved.rows == expected
    assert call_count["count"] == 12
    assert board.rows == original_rows
    assert_no_empty_cells(resolved)
    assert_no_matches(resolved)


def test_overlapping_matches_resolve_across_cascade() -> None:
    """Overlapping matches are cleared and resolved correctly."""

    rows = [
        [GemType.RED, GemType.RED, GemType.RED],
        [GemType.BLUE, GemType.RED, GemType.BLUE],
        [GemType.BLUE, GemType.RED, GemType.BLUE],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows
    supplier, call_count = make_supplier([
        GemType.RED,
        GemType.GREEN,
        GemType.YELLOW,
        GemType.PURPLE,
        GemType.ORANGE,
    ])

    resolved = resolve_cascades(board, supplier)

    expected = (
        (GemType.BLUE, GemType.PURPLE, GemType.BLUE),
        (GemType.BLUE, GemType.YELLOW, GemType.BLUE),
        (GemType.RED, GemType.GREEN, GemType.ORANGE),
    )
    assert resolved.rows == expected
    assert call_count["count"] == 5
    assert board.rows == original_rows
    assert_no_empty_cells(resolved)
    assert_no_matches(resolved)


def test_deterministic_supplier_produces_same_output() -> None:
    """Same input and supplier sequence yield identical output."""

    rows = [
        [GemType.RED, GemType.RED, GemType.RED],
        [GemType.BLUE, GemType.GREEN, GemType.YELLOW],
        [GemType.PURPLE, GemType.ORANGE, GemType.BLUE],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows
    supplier_one, _ = make_supplier([
        GemType.RED,
        GemType.GREEN,
        GemType.PURPLE,
    ])
    supplier_two, _ = make_supplier([
        GemType.RED,
        GemType.GREEN,
        GemType.PURPLE,
    ])

    first = resolve_cascades(board, supplier_one)
    second = resolve_cascades(board, supplier_two)

    assert first == second
    assert board.rows == original_rows
    assert_no_empty_cells(first)
    assert_no_matches(first)


def test_empty_cells_without_matches_are_normalized() -> None:
    """Empty cells trigger gravity and refill even without matches."""

    rows = [
        [GemType.EMPTY, GemType.RED],
        [GemType.BLUE, GemType.GREEN],
        [GemType.YELLOW, GemType.PURPLE],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows
    supplier, call_count = make_supplier([GemType.ORANGE])

    resolved = resolve_cascades(board, supplier)

    expected = (
        (GemType.BLUE, GemType.RED),
        (GemType.YELLOW, GemType.GREEN),
        (GemType.ORANGE, GemType.PURPLE),
    )
    assert resolved.rows == expected
    assert call_count["count"] == 1
    assert board.rows == original_rows
    assert_no_empty_cells(resolved)
    assert_no_matches(resolved)
