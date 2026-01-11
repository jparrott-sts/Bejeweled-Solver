"""Cascade resolution for inverted gravity boards.

Purpose:
    Resolve all cascades by repeatedly applying match removal, gravity, and refill.
Inputs:
    BoardState instances and a deterministic gem supplier callable.
Outputs:
    New BoardState instances with no matches or empty cells remaining.
Assumptions:
    Match detection, removal, gravity, and refill are implemented elsewhere.
Limitations:
    No scoring, logging, or AI evaluation is performed.
"""

from __future__ import annotations

from collections.abc import Callable

from game.board import BoardState
from game.gem import GemType
from game.gravity import apply_gravity
from game.refill import refill_board
from game.rules import find_matches, remove_matches


def resolve_cascades(board: BoardState, gem_supplier: Callable[[], GemType]) -> BoardState:
    """Return a new board with all cascades resolved.

    Args:
        board: The starting board state.
        gem_supplier: Callable that provides a GemType for refills.
    """

    current = board
    while True:
        settled = apply_gravity(current)
        refilled = refill_board(settled, gem_supplier)
        matches = find_matches(refilled)
        if not matches:
            return refilled
        current = remove_matches(refilled, matches)
