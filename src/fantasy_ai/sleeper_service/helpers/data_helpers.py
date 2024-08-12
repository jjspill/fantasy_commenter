import json

import aiohttp
from google.cloud import firestore

db = firestore.Client()


def sleeper_checks(player_info):
    if "sportradar_id" not in player_info or not player_info["sportradar_id"]:
        return False

    if "team" not in player_info or not player_info["team"]:
        return False

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
            data = await response.json()
            return data


async def upload_sleeper_data(data):
    batch = db.batch()
    player_info_col_ref = db.collection("player_info")
    for player_id, player_info in data.items():
        if not sleeper_checks(player_info):
            continue

        id = player_info["sportradar_id"]
        player_doc_ref = player_info_col_ref.document(id)
        batch.set(player_doc_ref, player_info)

    batch.commit()


def build_player_map(data):
    player_map = {}
    for player_id, player_info in data.items():
        if not sleeper_checks(player_info):
            continue
        player_map[player_info["search_full_name"]] = player_info["sportradar_id"]

    with open("player_map.json", "w") as f:
        json.dump(player_map, f)

    return player_map
