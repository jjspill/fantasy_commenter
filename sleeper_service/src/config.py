from enum import Enum

RELEVANT_POSITIONS = ["QB", "RB", "WR", "TE", "K", "DEF"]


class Mode(Enum):
    NEWS = 1
    NEWS_STATS = 2
    ALL_TIME = 3
