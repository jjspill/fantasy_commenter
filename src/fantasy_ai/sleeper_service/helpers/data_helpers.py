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


def sleeper_checks(player_info):
    if "sportradar_id" not in player_info or not player_info["sportradar_id"]:
        return False

    # if "team" not in player_info or not player_info["team"]:
    #     return False

    if "fantasy_positions" not in player_info or not player_info["fantasy_positions"]:
        return False

    if player_info["fantasy_positions"][0] not in [
        "QB",
        "RB",
        "WR",
        "TE",
        "k",
    ]:
        return False

    if "search_full_name" not in player_info or not player_info["search_full_name"]:
        return False

    return True


async def fetch_player_data():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.sleeper.app/v1/players/nfl") as response:
            if response.status == 200:
                data = await response.json()
                filtered_data = {
                    player_id: info
                    for player_id, info in data.items()
                    if sleeper_checks(info)
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
