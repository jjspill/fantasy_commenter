from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List, Optional


@dataclass
class SleeperNews:
    title: str
    description: str
    published_date: int
    source: str
    url: Optional[str] = field(default=None)
    analysis: Optional[str] = field(default=None)


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


def is_within_last_24_hours(unix_timestamp):
    timestamp_time = datetime.fromtimestamp(unix_timestamp / 1000, tz=timezone.utc)
    current_utc_time = datetime.now(timezone.utc)
    return (current_utc_time - timestamp_time) < timedelta(days=1)


def extract_news(data):
    news_items = data["data"]["get_player_news"]
    extracted_news = []

    for item in news_items:
        title = item["metadata"].get("title")
        description = item["metadata"].get("description")
        published_date = item.get("published")
        source = item.get("source")
        url = item["metadata"].get("url", None)
        analysis = item["metadata"].get("analysis", None)

        # if not is_within_last_24_hours(published_date):
        #     continue

        news = SleeperNews(
            title=title,
            description=description,
            published_date=published_date,
            source=source,
            url=url,
            analysis=analysis,
        )
        extracted_news.append(news)

    return extracted_news


def extract_sleeper_profile(data: dict) -> SleeperProfile:
    return SleeperProfile(
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        sleeper_id=data.get("player_id"),
        sportradar_id=data.get("sportradar_id"),
        years_exp=data.get("years_exp"),
        position=data.get("position"),
        age=data.get("age"),
        team=data.get("team"),
        height=data.get("height"),
        weight=data.get("weight"),
        college=data.get("college"),
        number=int(data.get("number")) if data.get("number") else None,
        rotowire_id=data.get("rotowire_id"),
        rotoworld_id=data.get("rotoworld_id"),
        swish_id=data.get("swish_id"),
        stats_id=data.get("stats_id"),
        espn_id=data.get("espn_id"),
        yahoo_id=data.get("yahoo_id"),
        fantasy_data_id=data.get("fantasy_data_id"),
        oddsjam_id=data.get("oddsjam_id"),
        gsis_id=data.get("gsis_id").strip() if data.get("gsis_id") else None,
        depth_chart_order=data.get("depth_chart_order"),
        injury_status=data.get("injury_status"),
        injury_body_part=data.get("injury_body_part"),
        injury_notes=data.get("injury_notes"),
        status=data.get("status"),
    )
