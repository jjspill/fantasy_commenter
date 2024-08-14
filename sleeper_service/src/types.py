from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SleeperNews:
    title: str
    description: str
    published_date: int
    source: str
    url: Optional[str] = None
    analysis: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class SleeperProfile:
    first_name: str
    last_name: str
    sleeper_id: str
    sportradar_id: str
    years_exp: int
    position: str
    age: int
    team: str
    height: Optional[str] = None
    weight: Optional[str] = None
    college: Optional[str] = None
    number: Optional[int] = None
    rotowire_id: Optional[int] = None
    rotoworld_id: Optional[int] = None
    swish_id: Optional[int] = None
    stats_id: Optional[int] = None
    espn_id: Optional[int] = None
    yahoo_id: Optional[int] = None
    fantasy_data_id: Optional[int] = None
    oddsjam_id: Optional[int] = None
    gsis_id: Optional[int] = None
    depth_chart_order: Optional[int] = None
    injury_status: Optional[str] = None
    injury_body_part: Optional[str] = None
    injury_notes: Optional[str] = None
    status: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class SleeperHistoricalStats:
    player_id: str
    yearly_stats: Dict[int, Optional[Dict[str, Any]]] = field(default_factory=dict)
    weekly_stats: Dict[int, List[Optional[Dict[str, Any]]]] = field(
        default_factory=dict
    )

    def to_dict(self):
        # Check if there are no stats for the most recent years (2023 and 2022); return empty dict if true
        if not self.yearly_stats.get(2023) and not self.yearly_stats.get(2022):
            return {}

        return {
            "player_id": self.player_id,
            # Convert yearly stats to a dict, replacing None values with an empty dict
            "yearly_stats": {
                year: (y_stats if y_stats is not None else {})
                for year, y_stats in self.yearly_stats.items()
            },
            # Process weekly stats for each year
            "weekly_stats": {
                year: (
                    # List comprehension to process each week's stats
                    [w_stats if w_stats else {} for w_stats in week_stats]
                    # Check if there is at least one non-empty stats dict; if not, use an empty list
                    if any(w_stats for w_stats in week_stats)
                    else []
                )
                for year, week_stats in self.weekly_stats.items()
            },
        }


@dataclass
class SleeperPlayer:
    player_id: str
    player_profile: SleeperProfile
    player_news: List[SleeperNews]
    historical_stats: Optional[SleeperHistoricalStats] = None

    def to_dict(self):
        return {
            "player_id": self.player_id,
            "player_profile": self.player_profile.to_dict(),
            "player_news": [news.to_dict() for news in self.player_news],
            "historical_stats": (
                self.historical_stats.to_dict() if self.historical_stats else {}
            ),
        }
