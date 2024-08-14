import asyncio
from typing import Any, Dict, List

import aiohttp
from google.cloud import firestore

from src.config import Mode
from src.types import SleeperHistoricalStats, SleeperPlayer
from src.utils import (
    calc_most_recent_nfl_week,
    extract_news,
    extract_sleeper_profile,
    extract_stats,
    filter_players,
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

    async def fetch_data(self):
        await self._fetch_player_data()

    async def _create_player(self, player_id, player_info, session):
        profile = extract_sleeper_profile(player_info)
        historical_stats = None  # Default to None
        news = None
        prev_week_stats = None

        if self.mode == Mode.ALL_TIME:
            # print(f"Fetching all news and historical stats for {player_id}")
            news = await self._fetch_player_news(player_id, session)
            historical_stats = await self._fetch_player_historical_stats(
                player_id, session, profile.position
            )

        if self.mode == Mode.NEWS:
            # print(f"Fetching news for {player_id}")
            news = await self._fetch_player_news(player_id, session)

        if self.mode == Mode.NEWS_STATS:
            # print(f"Fetching news and stats for {player_id}")
            news = await self._fetch_player_news(player_id, session)
            prev_week_stats = await self._fetch_player_in_season_stats(
                player_id, session
            )

        return SleeperPlayer(
            player_id=player_id,
            player_profile=profile,
            player_news=news,
            historical_stats=historical_stats,
            prev_week_stats=prev_week_stats,
        )

    async def _fetch_player_data(self):
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
                    self.players = await asyncio.gather(*tasks)
                else:
                    raise Exception(f"Failed to fetch /players/nfl: {response.status}")

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

    async def _fetch_player_in_season_stats(self, player_id, session):
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

                if adj_week == None or (adj_week > 18 or adj_week < 1):
                    return None

                return await self._fetch_player_weekly_stats(
                    player_id, session, season, adj_week
                )
            else:
                print(
                    f"Failed to fetch player in-season stats for {player_id}: {response.status}"
                )

    async def _fetch_player_historical_stats(
        self, player_id, session
    ) -> SleeperHistoricalStats:
        print(f"Fetching historical stats for {player_id}")
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

    # async def upload_sleeper_data(self, data):
    #     batch = self.db.batch()
    #     player_info_col_ref = self.db.collection("player_info4")

    #     tasks = [
    #         self._handle_player_data(batch, player_info_col_ref, player_id, player_info)
    #         for player_id, player_info in data.items()
    #     ]
    #     await asyncio.gather(*tasks)
    #     batch.commit()

    # async def _handle_player_data(
    #     self, batch, player_info_col_ref, player_id, player_info
    # ):
    #     player_doc_ref = player_info_col_ref.document(player_id)
    #     batch.set(player_doc_ref, extract_sleeper_profile(player_info).to_dict())

    #     # Assuming fetch_player_news is defined to fetch news for a player
    #     player_news = await self.fetch_player_news(player_id)
    #     for news in player_news:
    #         news_doc_ref = player_doc_ref.collection("sleeper_news").document()
    #         batch.set(news_doc_ref, news.to_dict())

    def build_maps(self, data):
        # Implementation for building maps
        pass
