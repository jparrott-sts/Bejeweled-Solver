"""Gem types used in the symbolic board representation.

Inputs: None.
Outputs: GemType enumeration values.
Assumptions: Only normal gems are represented in this phase.
Limitations: Special gems are intentionally excluded.
"""

from __future__ import annotations

from enum import Enum, auto


class GemType(Enum):
    """Enumeration of normal gem types.

    Uses descriptive color names for easy extension without numeric magic values.
    """

    EMPTY = auto()
    RED = auto()
    BLUE = auto()
    GREEN = auto()
    YELLOW = auto()
    PURPLE = auto()
    ORANGE = auto()

    @property
    def is_matchable(self) -> bool:
        """Return whether this gem can participate in matches."""

        return self is not GemType.EMPTY
