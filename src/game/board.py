"""Immutable board representation for the game layer.

Purpose:
    Provide a deterministic, immutable container for gem positions.
Inputs:
    Rows of GemType values provided to the factory method.
Outputs:
    BoardState instances with fixed width and height.
Assumptions:
    Rows are rectangular and contain only GemType values.
Limitations:
    No game logic (matches, gravity, scoring) is implemented here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from game.gem import GemType

@dataclass(frozen=True)
class BoardState:
    """Immutable representation of a gem board."""

    rows: tuple[tuple[GemType, ...], ...]

    @property
    def width(self) -> int:
        """Width of the board in gems."""

        if not self.rows:
            return 0
        return len(self.rows[0])

    @property
    def height(self) -> int:
        """Height of the board in gems."""

        return len(self.rows)

    def get(self, x: int, y: int) -> GemType:
        """Return the gem at (x, y).

        Raises:
            IndexError: If the coordinate is outside the board bounds.
        """

        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise IndexError(f"Coordinate out of bounds: ({x}, {y})")
        return self.rows[y][x]

    @classmethod
    def from_rows(cls, rows: Sequence[Sequence[GemType]]) -> BoardState:
        """Create a BoardState from row data.

        Args:
            rows: A rectangular 2D sequence of GemType values.

        Raises:
            ValueError: If rows are empty or not rectangular.
        """

        if not rows:
            raise ValueError("Board must contain at least one row.")
        row_lengths = {len(row) for row in rows}
        if 0 in row_lengths:
            raise ValueError("Board rows must contain at least one gem.")
        if len(row_lengths) != 1:
            raise ValueError("Board rows must be rectangular.")
        frozen_rows = tuple(tuple(row) for row in rows)
        return cls(rows=frozen_rows)
