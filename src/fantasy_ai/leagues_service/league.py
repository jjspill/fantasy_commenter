import asyncio
import json
from dataclasses import asdict, dataclass

import aiohttp
from google.cloud import firestore

db = firestore.Client()


@dataclass
class SleeperRoster:
    league_id: str
    owner_id: str
    players: list
    roster_id: int
    wins: int
    losses: int
    ties: int


@dataclass
class SleeperLeague:
    name: str
    num_teams: int
    league_id: str
    total_rosters: int
    rosters: list[SleeperRoster]


async def fetch_league_info(league_id: str):
    """Fetches league data."""
    url = f"https://api.sleeper.app/v1/league/{league_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return None


async def fetch_rosters(league_id: str):
    """Fetches roster data for a league."""
    url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return None


async def create_league_dataclass(league_id: str):
    league_info = await fetch_league_info(league_id)
    rosters_data = await fetch_rosters(league_id)

    if league_info and rosters_data:
        rosters = [
            SleeperRoster(
                league_id=roster.get("league_id", ""),
                owner_id=roster.get("owner_id", ""),
                players=roster.get("players", []),
                roster_id=roster.get("roster_id", -1),
                wins=roster.get("settings", {}).get("wins", 0),
                losses=roster.get("settings", {}).get("losses", 0),
                ties=roster.get("settings", {}).get("ties", 0),
            )
            for roster in rosters_data
        ]

        league = SleeperLeague(
            name=league_info.get("name", "Unknown League"),
            num_teams=league_info.get("total_rosters", 0),
            league_id=league_id,
            total_rosters=len(rosters),
            rosters=rosters,
        )
        return league
    else:
        return "Failed to fetch league or roster data."


def upload_league_data(league: SleeperLeague):
    batch = db.batch()
    league_col_ref = db.collection("leagues")
    league_doc_ref = league_col_ref.document(league.league_id)

    # Set league metadata
    league_data = {k: v for k, v in asdict(league).items() if k != "rosters"}
    batch.set(league_doc_ref, league_data)

    # Set each roster as a document in the 'rosters' subcollection
    rosters_subcol_ref = league_doc_ref.collection("rosters")
    for roster in league.rosters:
        roster_doc_ref = rosters_subcol_ref.document(str(roster.roster_id))
        batch.set(roster_doc_ref, asdict(roster))

    batch.commit()


async def main():
    league_id = "1048791311114985472"
    league = await create_league_dataclass(league_id)
    print(json.dumps(league, default=lambda x: x.__dict__, indent=4))
    upload_league_data(league)


if __name__ == "__main__":
    asyncio.run(main())


# async def fetch_trades():
#     url = "https://sleeper.com/graphql"
#     headers = {
#         "Content-Type": "application/json",
#         "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9eyJhdmF0YXIiOm51bGwsImRpc3BsYXlfbmFtZSI6IkpKREFCT1NTIiwiZXhwIjoxNzU1MDIyOTIyLCJpYXQiOjE3MjM0ODY5MjIsImlzX2JvdCI6ZmFsc2UsImlzX21hc3RlciI6ZmFsc2UsInJlYWxfbmFtZSI6bnVsbCwidXNlcl9pZCI6NjAyMjM3MDE2Mzk4MTU5ODcyLCJ2YWxpZF8yZmEiOiIifQ.Mw4KabMAQgO_5s6lM6mGxzV4V4oebW5iilMeQFeFB8s",
#         "referer": "https://sleeper.com/leagues/1062808704719990784/trades",
#     }
#     payload = {
#         "operationName": "league_transactions_filtered",
#         "variables": {},
#         "query": f"""
#         query league_transactions_filtered {{
#             league_transactions_filtered(league_id: "1062808704719990784",roster_id_filters: [1],type_filters: ["trade"],leg_filters: [],status_filters: []){{
#                 adds
#                 consenter_ids
#                 created
#                 creator
#                 draft_picks
#                 drops
#                 league_id
#                 leg
#                 metadata
#                 roster_ids
#                 settings
#                 status
#                 status_updated
#                 transaction_id
#                 type
#                 player_map
#                 waiver_budget
#                 }}
#             }}
#         """,
#     }

#     async with aiohttp.ClientSession() as session:
#         async with session.post(url, headers=headers, json=payload) as response:
#             if response.status == 200:
#                 data = await response.json()
#                 return data
#             else:
#                 return f"Failed to fetch data: {response.status}"
