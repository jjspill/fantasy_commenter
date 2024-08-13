from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional


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
class SleeperWRYearlyStats:
    player_id: str
    team: str
    year: int
    position_rank_half_ppr: int
    position_rank_ppr: int
    position_rank_std: int
    pts_half_ppr: float
    pts_ppr: float
    pts_std: float
    rank_half_ppr: int
    rank_ppr: int
    rank_std: int
    receptions: int
    receiving_yards: int
    receiving_touchdowns: int
    longest_reception: int
    receiving_targets: int
    receiving_yards_per_target: float
    rushing_and_receiving_yards: int

    def to_dict(self):
        return asdict(self)


@dataclass
class SleeperWRStatsWeekly:
    player_id: str
    week: int
    season: int
    team: str
    opponent: str
    pts_half_ppr: float
    pts_ppr: float
    pts_std: float
    pos_rank_half_ppr: int
    pos_rank_ppr: int
    pos_rank_std: int
    offensive_snaps: int
    penalties: int
    penalty_yards: int
    rec: int
    rec_0_4_yards: int
    rec_5_9_yards: int
    rec_10_19_yards: int
    rec_20_29_yards: int
    rec_30_39_yards: int
    rec_40_plus_yards: int
    rec_air_yards: int
    rec_drop: int
    rec_first_down: int
    rec_long: int
    rec_targets: int
    rec_redzone_targets: int
    rec_td: int
    rec_td_long: int
    rec_yards: int
    rec_yac: int
    rec_yards_per_rec: float
    rec_yards_per_target: float
    rush_and_rec_yards: int

    def to_dict(self):
        return asdict(self)


@dataclass
class SleeperHistoricalStats:
    player_id: str
    yearly_stats: Dict[int, Optional[SleeperWRYearlyStats]] = field(
        default_factory=dict
    )
    weekly_stats: Dict[int, List[Optional[SleeperWRStatsWeekly]]] = field(
        default_factory=dict
    )

    def to_dict(self):
        return {
            "player_id": self.player_id,
            "yearly_stats": {
                year: (y_stats.to_dict() if y_stats else {})
                for year, y_stats in self.yearly_stats.items()
            },
            "weekly_stats": {
                year: [w_stats.to_dict() if w_stats else {} for w_stats in week_stats]
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
