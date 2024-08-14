import json
from datetime import datetime, timedelta, timezone

import pytz

from src.config import RELEVANT_POSITIONS, Mode
from src.types import SleeperNews, SleeperPlayer, SleeperProfile


def get_current_year():
    return datetime.now().year


def calc_mode(mode: Mode) -> Mode:
    """
    Normally just get weekly news, but if it's Tuesday, get the prior week's player stats as well.
    """
    if mode == Mode.ALL_TIME:
        return Mode.ALL_TIME

    time_est = datetime.now(pytz.utc).astimezone(pytz.timezone("US/Eastern"))
    is_tuesday = time_est.weekday() == 1

    if mode == Mode.NEWS and is_tuesday:
        print("It's Tuesday, fetching stats for the previous week.")
        return Mode.NEWS_STATS


def filter_players(player_info):
    """
    Ensures that player info contains required keys and values:
    - 'sportradar_id' and 'full_name' must not be None.
    - 'fantasy_positions' must include at least one position from RELEVANT_POSITIONS.
    - 'search_rank' must not be 9999999 or None.
    """
    try:
        fantasy_positions = player_info.get("fantasy_positions")
        if fantasy_positions is None:
            fantasy_positions = []

        if (
            player_info.get("sportradar_id") is None
            or player_info.get("full_name") is None
            or player_info.get("search_rank") is None
            or player_info.get("search_rank") == 9999999
            or not any(pos in RELEVANT_POSITIONS for pos in fantasy_positions)
        ):
            return False

        return True

    except Exception as e:
        print(f"Error filtering player {player_info}: {e}")
        return False


def is_within_last_24_hours(unix_timestamp):
    timestamp_time = datetime.fromtimestamp(unix_timestamp / 1000, tz=timezone.utc)
    current_utc_time = datetime.now(timezone.utc)
    return (current_utc_time - timestamp_time) < timedelta(days=1)


def extract_news(data, mode: Mode):
    news_items = data["data"]["get_player_news"]
    extracted_news = []

    for item in news_items:
        title = item["metadata"].get("title")
        description = item["metadata"].get("description")
        published_date = item.get("published")
        source = item.get("source")
        url = item["metadata"].get("url", None)
        analysis = item["metadata"].get("analysis", None)

        # If mode is not ALL_TIME, only include news from the last 24 hours
        if mode != Mode.ALL_TIME and not is_within_last_24_hours(published_date):
            continue

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


def extract_stats(data, week=None):
    if not data:
        return {}

    if week:
        return extract_all_weekly_stats(data, week)
    else:
        return extract_all_yearly_stats(data)


def extract_all_weekly_stats(data, week):
    if not data:
        return {}

    stats = data.get("stats", {})

    if stats.get("gp", 0) == 0:
        return {}

    stats["season"] = data.get("season")
    stats["week"] = week
    stats["team"] = data.get("team")
    stats["opponent"] = data.get("opponent")

    return stats


def extract_all_yearly_stats(data):
    if not data:
        return {}

    stats = data.get("stats", {})
    stats["season"] = data.get("season")
    stats["team"] = data.get("team")

    return stats


def calc_most_recent_nfl_week(week: int, season_type: str) -> int | None:
    if season_type == "post" and week == 1:
        return 18
    elif season_type == "regular" and week > 1:
        return week - 1
    else:
        return None


def write_players_to_json(players: list[SleeperPlayer]):
    with open("players.json", "w") as f:
        f.write(json.dumps([player.to_dict() for player in players], indent=4))
