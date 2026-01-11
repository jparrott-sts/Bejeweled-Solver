"""Tests for deterministic refill logic."""

# ruff: noqa: E402

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from game.board import BoardState
from game.gem import GemType
from game.refill import refill_board
import pytest


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


def test_single_empty_cell_at_bottom() -> None:
    """Refills a single empty cell at the bottom of a column."""

    rows = [
        [GemType.RED],
        [GemType.BLUE],
        [GemType.EMPTY],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows
    supplier, call_count = make_supplier([GemType.GREEN])

    updated = refill_board(board, supplier)

    expected = (
        (GemType.RED,),
        (GemType.BLUE,),
        (GemType.GREEN,),
    )
    assert updated.rows == expected
    assert call_count["count"] == 1
    assert board.rows == original_rows


def test_multiple_empty_cells_fill_bottom_up() -> None:
    """Refills multiple empty cells in a column from bottom to top."""

    rows = [
        [GemType.EMPTY],
        [GemType.RED],
        [GemType.EMPTY],
        [GemType.EMPTY],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows
    supplier, call_count = make_supplier([
        GemType.GREEN,
        GemType.BLUE,
        GemType.YELLOW,
    ])

    updated = refill_board(board, supplier)

    expected = (
        (GemType.YELLOW,),
        (GemType.RED,),
        (GemType.BLUE,),
        (GemType.GREEN,),
    )
    assert updated.rows == expected
    assert call_count["count"] == 3
    assert board.rows == original_rows


def test_mixed_columns_refill_only_empty_cells() -> None:
    """Refills only empty cells while preserving existing gems."""

    rows = [
        [GemType.RED, GemType.EMPTY],
        [GemType.EMPTY, GemType.BLUE],
        [GemType.GREEN, GemType.EMPTY],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows
    supplier, call_count = make_supplier([
        GemType.YELLOW,
        GemType.PURPLE,
        GemType.BLUE,
    ])

    updated = refill_board(board, supplier)

    expected = (
        (GemType.RED, GemType.BLUE),
        (GemType.YELLOW, GemType.BLUE),
        (GemType.GREEN, GemType.PURPLE),
    )
    assert updated.rows == expected
    assert call_count["count"] == 3
    assert board.rows == original_rows


def test_no_empty_cells_returns_identical_board() -> None:
    """Boards with no empty cells are returned unchanged."""

    rows = [
        [GemType.RED, GemType.BLUE],
        [GemType.GREEN, GemType.YELLOW],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows
    supplier, call_count = make_supplier([])

    updated = refill_board(board, supplier)

    expected = (
        (GemType.RED, GemType.BLUE),
        (GemType.GREEN, GemType.YELLOW),
    )
    assert updated.rows == expected
    assert call_count["count"] == 0
    assert board.rows == original_rows


def test_deterministic_supplier_order_is_respected() -> None:
    """Supplier order is consumed deterministically during refill."""

    rows = [
        [GemType.EMPTY, GemType.EMPTY],
        [GemType.EMPTY, GemType.EMPTY],
    ]
    board = BoardState.from_rows(rows)
    original_rows = board.rows
    supplier, call_count = make_supplier([
        GemType.RED,
        GemType.BLUE,
        GemType.GREEN,
        GemType.YELLOW,
    ])

    updated = refill_board(board, supplier)

    expected = (
        (GemType.BLUE, GemType.YELLOW),
        (GemType.RED, GemType.GREEN),
    )
    assert updated.rows == expected
    assert call_count["count"] == 4
    assert board.rows == original_rows


def test_supplier_returning_empty_raises_error() -> None:
    """Refill should reject suppliers that return empty gems."""

    rows = [
        [GemType.EMPTY],
    ]
    board = BoardState.from_rows(rows)

    def supplier() -> GemType:
        return GemType.EMPTY

    with pytest.raises(ValueError, match="gem_supplier\\(\\) returned GemType\\.EMPTY"):
        refill_board(board, supplier)
