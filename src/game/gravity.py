"""Inverted gravity resolution for the game layer.

Purpose:
    Apply upward gravity to a BoardState by moving gems toward the top.
Inputs:
    BoardState instances with GemType values, including GemType.EMPTY.
Outputs:
    New BoardState instances with gems shifted upward and empties at the bottom.
Assumptions:
    BoardState is rectangular and immutable.
Limitations:
    No cascades, refills, or scoring are handled here.
"""

from __future__ import annotations

from game.board import BoardState
from game.gem import GemType


def apply_gravity(board: BoardState) -> BoardState:
    """Return a new board after applying inverted (upward) gravity."""

    height = board.height
    width = board.width
    columns: list[list[GemType]] = []
    for x in range(width):
        column = [board.get(x, y) for y in range(height)]
        non_empty = [gem for gem in column if gem is not GemType.EMPTY]
        empty_count = height - len(non_empty)
        columns.append(non_empty + [GemType.EMPTY] * empty_count)

    rows = tuple(
        tuple(columns[x][y] for x in range(width))
        for y in range(height)
    )
    return BoardState(rows=rows)
