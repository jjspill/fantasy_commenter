import asyncio
from typing import Any, Dict, List, Optional

import aiohttp
from google.cloud import firestore

from src.config import Mode
from src.types import (
    SleeperHistoricalStats,
    SleeperNews,
    SleeperPlayer,
    SleeperPrevWeekStats,
)
from src.utils import (
    calc_most_recent_nfl_week,
    extract_news,
    extract_sleeper_profile,
    extract_stats,
    filter_players,
    get_current_year,
)

## Thinking
## Fetch all the data from sleeper APIs
## Filter the players
## For each player, fetch their news (incorporate mode)
## For each player, fetch their stats (incorporate mode -> have to figure out when weekly stats update, only fetch them on that date...)
## Process the data
## Upload the data to firestore


class SleeperAPIClient:
    def __init__(self, mode: Mode):
        self.db: firestore.Client = firestore.Client()
        self.mode: Mode = mode
        self.players: list[SleeperPlayer] = []

    async def fetch_player_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.sleeper.app/v1/players/nfl"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    tasks = [
                        self._create_player(player_id, player_info, session)
                        for player_id, player_info in data.items()
                        if filter_players(player_info)
                    ]
                    tasks = tasks[:10]
                    self.players = await asyncio.gather(*tasks)
                else:
                    raise Exception(f"Failed to fetch /players/nfl: {response.status}")

    async def upload_sleeper_data(self):
        print("Uploading player data...")
        tasks = []
        for player in self.players:
            tasks.append(self._process_player(player))
        await asyncio.gather(*tasks)

    async def _process_player(self, player):
        player_ref = self.db.collection("player_info").document(player.player_id)
        player_ref.set(player.player_profile.to_dict())

        if player.player_news:
            self._upload_news(player_ref, player.player_news)

        if player.historical_stats:
            self._upload_stats(player_ref, player.historical_stats, "historical_stats")

        if player.prev_week_stats and player.prev_week_stats.stats:
            self._upload_stats(player_ref, player.prev_week_stats, "prev_week_stats")

    def _upload_news(self, player_ref, news_list):
        news_ref = player_ref.collection("sleeper_news")
        for news in news_list:
            news_ref.document().set(news.to_dict())

    def _upload_stats(self, player_ref, stats, stats_type):
        stats_ref = player_ref.collection("sleeper_stats")
        if stats_type == "prev_week_stats":
            year = get_current_year()
            year_doc_ref = stats_ref.document(str(year))
            weeks_ref = year_doc_ref.collection("weeks")
            week_index = stats.stats.get("week")
            weeks_ref.document(str(week_index)).set(stats.stats)
        else:
            # Assuming stats are separated by year and then by week
            for year, year_stats in stats.yearly_stats.items():
                if not year_stats:  # Skip a year with no stats
                    continue
                year_doc_ref = stats_ref.document(str(year))
                year_doc_ref.set({"yearly_stats": year_stats})
                if (
                    year in stats.weekly_stats
                    and stats.weekly_stats[year]
                    and len(stats.weekly_stats[year])  # Check if year has weekly stats
                ):
                    if isinstance(
                        stats.weekly_stats[year], list
                    ):  # Each week as a subdocument
                        weeks_ref = year_doc_ref.collection("weeks")
                        for week_stats in stats.weekly_stats[year]:
                            if week_stats:
                                week_index = week_stats.get("week")
                                weeks_ref.document(str(week_index)).set(week_stats)
                    else:  # All weeks in a single field
                        year_doc_ref.update({"weekly_stats": stats.weekly_stats[year]})

    async def _create_player(self, player_id, player_info, session):
        # Extract the profile data
        profile = extract_sleeper_profile(player_info)

        news: Optional[List[SleeperNews]] = []
        historical_stats: Optional[SleeperHistoricalStats] = None
        prev_week_stats: Optional[SleeperPrevWeekStats] = None

        # Conditional fetching based on mode
        if self.mode == Mode.ALL_TIME:
            # Fetch all-time relevant data
            news = await self._fetch_player_news(player_id, session)
            historical_stats = await self._fetch_player_historical_stats(
                player_id, session
            )
        elif self.mode == Mode.NEWS:
            # Fetch only news
            news = await self._fetch_player_news(player_id, session)
        elif self.mode == Mode.NEWS_STATS:
            # Fetch both news and current season stats
            news = await self._fetch_player_news(player_id, session)
            prev_week_stats = await self._fetch_player_prev_week_stats(
                player_id, session
            )

        # Return a fully constructed SleeperPlayer object
        return SleeperPlayer(
            player_id=player_id,
            player_profile=profile,
            player_news=news,
            historical_stats=historical_stats,
            prev_week_stats=prev_week_stats,
        )

    async def _fetch_player_news(self, player_id, session):
        url = "https://sleeper.com/graphql"
        headers = {"Content-Type": "application/json"}
        payload = {
            "operationName": "get_player_news",
            "variables": {},
            "query": f"""
            query get_player_news {{
                get_player_news(sport: "nfl", player_id: "{player_id}", limit: 10) {{
                    metadata
                    player_id
                    published
                    source
                    source_key
                    sport
                }}
            }}
            """,
        }

        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                extracted_news = extract_news(data, self.mode)
                return extracted_news
            else:
                print(f"Failed to fetch player news for {player_id}: {response.status}")

    async def _fetch_player_prev_week_stats(self, player_id, session):
        """
        Fetches statistics for a player for the prior week. This is used to get the most recent stats for a player.
        - Have to calculate when its postseason week 1 and fetch the stats for the last week of the regular season
        """
        nfl_state_url = "https://api.sleeper.app/v1/state/nfl"
        async with session.get(nfl_state_url) as response:
            if response.status == 200:
                data = await response.json()
                season = data.get("season")
                week = data.get("week")
                season_type = data.get("season_type")

                adj_week = calc_most_recent_nfl_week(week, season_type)
                print(f"Fetching in-season stats for {player_id} week {adj_week}")

                if adj_week == None or (adj_week > 18 or adj_week < 1):
                    return None

                stats = await self._fetch_player_weekly_stats(
                    player_id, session, season, adj_week
                )
                return SleeperPrevWeekStats(stats=stats)

            else:
                print(
                    f"Failed to fetch player in-season stats for {player_id}: {response.status}"
                )

    async def _fetch_player_historical_stats(
        self, player_id, session
    ) -> SleeperHistoricalStats:
        historical_stats = SleeperHistoricalStats(player_id=player_id)

        # fetch yearly stats for the last 5 years
        # fetch weekly stats for weeks 1-18
        for year in range(2019, 2024):
            yearly_stats = (
                await self._fetch_player_yearly_stats(player_id, session, year) or None
            )
            weekly_stats = []

            for week in range(1, 19):
                week_stats = (
                    await self._fetch_player_weekly_stats(
                        player_id, session, year, week
                    )
                    or None
                )
                # print(f"Player {player_id} week {week} stats: {week_stats}")
                weekly_stats.append(week_stats)

            historical_stats.yearly_stats[year] = yearly_stats
            historical_stats.weekly_stats[year] = weekly_stats

        return historical_stats

    async def _fetch_player_weekly_stats(
        self,
        player_id,
        session,
        season: int,
        week: int,
    ) -> List[Dict[str, Any]]:
        url = f"https://api.sleeper.com/stats/nfl/player/{player_id}?season_type=regular&season={season}&grouping=week"

        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return extract_stats(data.get(str(week), {}), week=week)
            else:
                print(
                    f"Failed to fetch player weekly stats for {player_id}: {response.status}"
                )

    async def _fetch_player_yearly_stats(
        self,
        player_id,
        session,
        season: int,
    ) -> Dict[str, Any]:
        url = f"https://api.sleeper.com/stats/nfl/player/{player_id}?season_type=regular&season={season}&grouping=year"

        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return extract_stats(data)
            else:
                print(
                    f"Failed to fetch player yearly stats for {player_id}: {response.status}"
                )

    def build_maps(self, data):
        # Implementation for building maps
        pass
