"""Match detection rules for the game layer.

Purpose:
    Detect contiguous horizontal and vertical matches of gems.
Inputs:
    BoardState instances.
Outputs:
    Sets of board coordinates representing matched gems.
Assumptions:
    BoardState is rectangular and immutable.
Limitations:
    No scoring, gravity, or cascade logic is implemented.
"""

from __future__ import annotations

from typing import TypeAlias

from game.board import BoardState

Coordinate: TypeAlias = tuple[int, int]

MIN_MATCH_LENGTH = 3


def find_matches(board: BoardState) -> set[Coordinate]:
    """Return all coordinates that are part of a match."""

    matches: set[Coordinate] = set()
    _add_horizontal_matches(board, matches)
    _add_vertical_matches(board, matches)
    return matches


def _add_horizontal_matches(board: BoardState, matches: set[Coordinate]) -> None:
    """Add horizontal matches to the provided set."""

    for y in range(board.height):
        x = 0
        while x < board.width:
            current = board.get(x, y)
            run_end = x + 1
            while run_end < board.width and board.get(run_end, y) == current:
                run_end += 1
            run_length = run_end - x
            if current.is_matchable and run_length >= MIN_MATCH_LENGTH:
                for match_x in range(x, run_end):
                    matches.add((match_x, y))
            x = run_end


def _add_vertical_matches(board: BoardState, matches: set[Coordinate]) -> None:
    """Add vertical matches to the provided set."""

    for x in range(board.width):
        y = 0
        while y < board.height:
            current = board.get(x, y)
            run_end = y + 1
            while run_end < board.height and board.get(x, run_end) == current:
                run_end += 1
            run_length = run_end - y
            if current.is_matchable and run_length >= MIN_MATCH_LENGTH:
                for match_y in range(y, run_end):
                    matches.add((x, match_y))
            y = run_end
