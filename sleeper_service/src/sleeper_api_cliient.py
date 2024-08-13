import asyncio

import aiohttp
from google.cloud import firestore

from src.config import Mode
from src.types import SleeperPlayer
from src.utils import extract_news, extract_sleeper_profile, filter_players

## Thinking
## Fetch all the data from sleeper APIs
## Filter the players
## For each player, fetch their news (incorporate mode)
## For each player, fetch their stats
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
        print("Fetching player news for", player_id)
        profile = extract_sleeper_profile(player_info)
        news = await self._fetch_player_news(player_id, session)
        return SleeperPlayer(
            player_id=player_id, player_profile=profile, player_news=news
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
