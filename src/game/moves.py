"""Legal move enumeration for the game layer.

Purpose:
    Provide deterministic enumeration of adjacent, non-empty gem swaps.
Inputs:
    BoardState instances containing GemType values.
Outputs:
    Ordered lists of legal swap coordinate pairs.
Assumptions:
    BoardState coordinates are zero-indexed (x, y).
Limitations:
    Does not evaluate match creation or simulate any game rules.
"""

from __future__ import annotations

from typing import Iterable

from game.board import BoardState
from game.gem import GemType
from game.rules import find_matches

Coordinate = tuple[int, int]
Swap = tuple[Coordinate, Coordinate]

RIGHT_OFFSET: Coordinate = (1, 0)
DOWN_OFFSET: Coordinate = (0, 1)


def enumerate_swaps(board: BoardState) -> list[Swap]:
    """Return all structurally legal adjacent swaps on the board.

    Legal swaps are orthogonally adjacent gem pairs where both cells are non-empty.
    Each swap is listed once using a stable row-major ordering of source cells,
    checking right neighbors before down neighbors.
    """

    swaps: list[Swap] = []
    for y in range(board.height):
        for x in range(board.width):
            if board.get(x, y) is GemType.EMPTY:
                continue
            swaps.extend(_enumerate_adjacent_swaps(board, x, y))
    return swaps


def is_productive_swap(board: BoardState, swap: Swap) -> bool:
    """Return True if the swap creates at least one match.

    Productive swaps are evaluated only on the immediate post-swap board.
    """

    (first_x, first_y), (second_x, second_y) = swap
    if board.get(first_x, first_y) is GemType.EMPTY:
        return False
    if board.get(second_x, second_y) is GemType.EMPTY:
        return False
    swapped_board = _apply_swap(board, swap)
    return bool(find_matches(swapped_board))


def filter_productive_swaps(board: BoardState, swaps: list[Swap]) -> list[Swap]:
    """Return only the swaps that create at least one match."""

    return [swap for swap in swaps if is_productive_swap(board, swap)]


def _apply_swap(board: BoardState, swap: Swap) -> BoardState:
    """Return a new board with the swap applied."""

    (first_x, first_y), (second_x, second_y) = swap
    first_gem = board.get(first_x, first_y)
    second_gem = board.get(second_x, second_y)
    rows = tuple(
        tuple(
            second_gem
            if (x, y) == (first_x, first_y)
            else first_gem
            if (x, y) == (second_x, second_y)
            else board.get(x, y)
            for x in range(board.width)
        )
        for y in range(board.height)
    )
    return BoardState(rows=rows)


def _enumerate_adjacent_swaps(board: BoardState, x: int, y: int) -> Iterable[Swap]:
    """Yield legal swaps for a single coordinate.

    Right and down directions are used to avoid duplicate swaps.
    """

    neighbors = (
        (RIGHT_OFFSET, (x + RIGHT_OFFSET[0], y + RIGHT_OFFSET[1])),
        (DOWN_OFFSET, (x + DOWN_OFFSET[0], y + DOWN_OFFSET[1])),
    )
    for _, (neighbor_x, neighbor_y) in neighbors:
        if _is_in_bounds(board, neighbor_x, neighbor_y):
            if board.get(neighbor_x, neighbor_y) is not GemType.EMPTY:
                yield (x, y), (neighbor_x, neighbor_y)


def _is_in_bounds(board: BoardState, x: int, y: int) -> bool:
    """Return True if the coordinate is inside the board bounds."""

    return 0 <= x < board.width and 0 <= y < board.height
