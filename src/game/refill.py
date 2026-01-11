"""Deterministic refill logic for inverted gravity boards.

Purpose:
    Fill GemType.EMPTY cells using a caller-supplied gem source.
Inputs:
    BoardState instances and a gem supplier callable.
Outputs:
    New BoardState instances with empty slots refilled bottom-up.
Assumptions:
    BoardState is rectangular and immutable.
Limitations:
    Does not apply gravity, detect matches, or resolve cascades.
"""

from __future__ import annotations

from collections.abc import Callable

from game.board import BoardState
from game.gem import GemType


def refill_board(board: BoardState, gem_supplier: Callable[[], GemType]) -> BoardState:
    """Return a new board with empty cells refilled bottom-up.

    Args:
        board: The board to refill.
        gem_supplier: Callable that provides a GemType per empty cell.
    """

    height = board.height
    width = board.width
    new_rows = [list(row) for row in board.rows]

    for x in range(width):
        for y in range(height - 1, -1, -1):
            if board.get(x, y) is GemType.EMPTY:
                supplied = gem_supplier()
                if supplied is GemType.EMPTY:
                    raise ValueError("gem_supplier() returned GemType.EMPTY during refill.")
                new_rows[y][x] = supplied

    return BoardState(rows=tuple(tuple(row) for row in new_rows))
