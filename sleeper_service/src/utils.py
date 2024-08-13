import json
from datetime import datetime, timedelta, timezone

from src.config import RELEVANT_POSITIONS, Mode
from src.types import (
    SleeperNews,
    SleeperPlayer,
    SleeperProfile,
    SleeperWRStatsWeekly,
    SleeperWRYearlyStats,
)


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

        # If mode is DAILY, only include news from the last 24 hours
        if mode == Mode.DAILY and not is_within_last_24_hours(published_date):
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


def extract_stats(data, position, week=None):
    print(f"Extracting stats for {position} player for week {week}")
    if not data:
        return {}

    if week:
        return extract_weekly_wr_stats(data, week)
    else:
        return extract_yearly_wr_stats(data)


def extract_yearly_wr_stats(data):
    stats = data.get("stats")
    if not stats:
        return {}

    return SleeperWRYearlyStats(
        player_id=data.get("player_id", "Unknown"),
        team=data.get("team", "Unknown"),  # Assuming 'team' is top-level in the data
        year=int(
            data.get("season", 0)
        ),  # Assuming 'season' is top-level and an integer year
        position_rank_half_ppr=stats.get("pos_rank_half_ppr", 0),
        position_rank_ppr=stats.get("pos_rank_ppr", 0),
        position_rank_std=stats.get("pos_rank_std", 0),
        pts_half_ppr=stats.get("pts_half_ppr", 0.0),
        pts_ppr=stats.get("pts_ppr", 0.0),
        pts_std=stats.get("pts_std", 0.0),
        rank_half_ppr=stats.get("rank_half_ppr", 0),
        rank_ppr=stats.get("rank_ppr", 0),
        rank_std=stats.get("rank_std", 0),
        receptions=stats.get("rec", 0),
        receiving_yards=stats.get("rec_yd", 0),
        receiving_touchdowns=stats.get("rec_td", 0),
        longest_reception=stats.get("rec_lng", 0),
        receiving_targets=stats.get("rec_tgt", 0),
        receiving_yards_per_target=stats.get("rec_ypt", 0.0),
        rushing_and_receiving_yards=stats.get("rush_rec_yd", 0),
    )


def extract_weekly_wr_stats(week_data, week):
    print(f"Extracting weekly stats for week {week}")
    print(f"Week data: {week_data}")
    if not week_data:
        return None

    stats = week_data["stats"]
    return SleeperWRStatsWeekly(
        player_id=week_data.get("player_id", "Unknown"),
        week=week,
        season=int(week_data["season"]),
        team=week_data["team"],
        opponent=week_data["opponent"],
        pts_half_ppr=float(stats.get("pts_half_ppr", 0.0)),
        pts_ppr=float(stats.get("pts_ppr", 0.0)),
        pts_std=float(stats.get("pts_std", 0.0)),
        pos_rank_half_ppr=stats.get("pos_rank_half_ppr", 0),
        pos_rank_ppr=stats.get("pos_rank_ppr", 0),
        pos_rank_std=stats.get("pos_rank_std", 0),
        offensive_snaps=stats.get("off_snp", 0),
        penalties=stats.get("penalty", 0),
        penalty_yards=stats.get("penalty_yd", 0),
        rec=stats.get("rec", 0),
        rec_0_4_yards=stats.get("rec_0_4", 0),
        rec_5_9_yards=stats.get("rec_5_9", 0),
        rec_10_19_yards=stats.get("rec_10_19", 0),
        rec_20_29_yards=stats.get("rec_20_29", 0),
        rec_30_39_yards=stats.get("rec_30_39", 0),
        rec_40_plus_yards=stats.get("rec_40p", 0),
        rec_air_yards=stats.get("rec_air_yd", 0),
        rec_drop=stats.get("rec_drop", 0),
        rec_first_down=stats.get("rec_fd", 0),
        rec_long=stats.get("rec_lng", 0),
        rec_targets=stats.get("rec_tgt", 0),
        rec_redzone_targets=stats.get("rec_rz_tgt", 0),
        rec_td=stats.get("rec_td", 0),
        rec_td_long=stats.get("rec_td_lng", 0),
        rec_yards=stats.get("rec_yd", 0),
        rec_yac=stats.get("rec_yar", 0),
        rec_yards_per_rec=float(stats.get("rec_ypr", 0.0)),
        rec_yards_per_target=float(stats.get("rec_ypt", 0.0)),
        rush_and_rec_yards=stats.get("rush_rec_yd", 0),
    )


def write_players_to_json(players: list[SleeperPlayer]):
    with open("players.json", "w") as f:
        f.write(json.dumps([player.to_dict() for player in players], indent=4))
