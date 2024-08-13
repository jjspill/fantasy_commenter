from enum import Enum

RELEVANT_POSITIONS = ["QB", "RB", "WR", "TE", "K", "DEF"]


class Mode(Enum):
    ALL_TIME = 1
    DAILY = 2
