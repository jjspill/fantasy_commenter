from dataclasses import asdict, dataclass, field
from typing import List, Optional


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
class SleeperPlayer:
    player_id: str
    player_profile: SleeperProfile
    player_news: List[SleeperNews]

    def to_dict(self):
        return {
            "player_id": self.player_id,
            "player_profile": self.player_profile.to_dict(),
            "player_news": [news.to_dict() for news in self.player_news],
        }
