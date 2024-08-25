import asyncio
import json

import aiohttp
from google.cloud import firestore

from fantasy_ai.sleeper_service.helpers.types import (
    SleeperNews,
    extract_news,
    extract_sleeper_profile,
)

db = firestore.Client()


RELEVANT_POSITIONS = ["QB", "RB", "WR", "TE", "K", "DEF"]


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


async def fetch_player_data():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.sleeper.app/v1/players/nfl") as response:
            if response.status == 200:
                data = await response.json()
                filtered_data = {
                    player_id: info
                    for player_id, info in data.items()
                    if filter_players(info)
                }
                return filtered_data
            else:
                return f"Failed to fetch data: {response.status}"


async def upload_sleeper_data(data):
    async with aiohttp.ClientSession() as session:  # Create a session
        batch = db.batch()
        player_info_col_ref = db.collection("player_info4")

        tasks = []
        for player_id, player_info in data.items():
            task = handle_player_data(
                session, batch, player_info_col_ref, player_id, player_info
            )
            tasks.append(task)

        # Await all tasks (fetching news and setting data)
        await asyncio.gather(*tasks)
        batch.commit()


async def handle_player_data(
    session, batch, player_info_col_ref, player_id, player_info
):
    player_news = await fetch_player_news(session, player_id)

    # id = player_info["sportradar_id"]
    extracted_info = extract_sleeper_profile(player_info)
    player_doc_ref = player_info_col_ref.document(player_id)
    batch.set(player_doc_ref, extracted_info.__dict__)

    for news in player_news:
        news_doc_ref = player_doc_ref.collection("sleeper_news").document()
        batch.set(news_doc_ref, news.__dict__)


def build_maps(data):
    player_map = {}
    sleeper_id_map = {}
    for player_id, player_info in data.items():
        player_map[player_info["search_full_name"]] = player_info["sportradar_id"]
        sleeper_id_map[player_info["sportradar_id"]] = player_id

    with open("player_name_map.py", "w") as f:
        f.write("player_name_map = " + repr(player_map) + "\n")

    with open("sleeper_id_map.py", "w") as f:
        f.write("sleeper_id_map = " + repr(sleeper_id_map) + "\n")


async def fetch_player_news(session, player_id):
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
            extracted_news = extract_news(data)
            return extracted_news
        else:
            return f"Failed to fetch data: {response.status}"
