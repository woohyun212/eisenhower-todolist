"""Common schemas and enums."""

from enum import Enum


class Quadrant(str, Enum):
    """Eisenhower Matrix quadrants."""

    DO = "DO"
    PLAN = "PLAN"
    DELEGATE = "DELEGATE"
    ELIMINATE = "ELIMINATE"
