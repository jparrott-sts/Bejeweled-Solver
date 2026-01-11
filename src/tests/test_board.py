"""Tests for the immutable BoardState representation."""

# ruff: noqa: E402

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from game.board import BoardState
from game.gem import GemType


def test_board_creation_and_dimensions() -> None:
    """BoardState should preserve dimensions and contents."""

    rows = [
        [GemType.RED, GemType.BLUE],
        [GemType.GREEN, GemType.YELLOW],
    ]
    board = BoardState.from_rows(rows)

    assert board.width == 2
    assert board.height == 2
    assert board.get(0, 0) is GemType.RED
    assert board.get(1, 1) is GemType.YELLOW


def test_board_is_immutable() -> None:
    """BoardState should prevent mutation after creation."""

    board = BoardState.from_rows([[GemType.RED]])
    with pytest.raises(FrozenInstanceError):
        board.rows = ((GemType.BLUE,),)


def test_get_out_of_bounds_raises() -> None:
    """Out-of-bounds access should raise IndexError."""

    board = BoardState.from_rows([[GemType.RED, GemType.BLUE]])
    with pytest.raises(IndexError):
        board.get(-1, 0)
    with pytest.raises(IndexError):
        board.get(2, 0)
    with pytest.raises(IndexError):
        board.get(0, 1)


def test_board_rejects_invalid_cells() -> None:
    """BoardState should reject rows with non-GemType cells."""

    rows = [
        [GemType.RED, None],
    ]
    with pytest.raises(ValueError, match="Invalid cells"):
        BoardState.from_rows(rows)
