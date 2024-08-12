import asyncio
import json

import aiohttp
from google.cloud import firestore

db = firestore.Client()


from google.cloud import firestore

db = firestore.Client()


def get_player_recent_news(player_doc_ref):
    news_query = (
        player_doc_ref.collection("sleeper_news")
        .order_by("publish_date", direction=firestore.Query.DESCENDING)
        .limit(5)
    )
    news_documents = news_query.stream()
    news_list = [
        doc.to_dict() for doc in news_documents
    ]  # Convert each document to dictionary
    return news_list


def get_player(player_id: str):
    player_doc_ref = db.collection("player_info4").document(player_id)
    news = get_player_recent_news(player_doc_ref)
    player_snapshot = player_doc_ref.get()
    if player_snapshot.exists:
        player_data = player_snapshot.to_dict()
    else:
        player_data = {}
    return {"player_data": player_data, "news": news}


def get_roster(league_id: str, team_id: int):
    team_doc_ref = (
        db.collection("leagues")
        .document(league_id)
        .collection("rosters")
        .document(str(team_id))
    )
    roster_snapshot = team_doc_ref.get()
    if roster_snapshot.exists:
        roster_data = roster_snapshot.to_dict()
    else:
        roster_data = {}
    return roster_data


def get_trade_specifics(league_id: str, trade_data):
    rosters = [
        get_roster(league_id, team_id)
        for team_id in trade_data.get("consenter_ids", [])
    ]
    players = [get_player(player_id) for player_id in trade_data.get("adds", {}).keys()]
    return {"rosters": rosters, "players": players}


async def get_trades(league_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.sleeper.app/v1/league/{league_id}/transactions/1"
        ) as response:
            if response.status == 200:
                data = await response.json()
                trades = []
                for transaction in data:
                    if transaction.get("type") == "trade":
                        trades.append(transaction)
                return trades
            else:
                return f"Failed to fetch data: {response.status}"


async def main():
    trades = await get_trades("1048791311114985472")
    if trades and len(trades) > 1:
        # Ensures that there is at least a second trade to process
        specifics = get_trade_specifics("1048791311114985472", trades[1])
        # Prepare the data to be dumped into JSON
        data_to_dump = {
            "trade_details": trades[
                1
            ],  # or any other trade details you want to include
            "specifics": specifics,
        }
        # Dumping the combined trade details and specifics to a file
        with open("trades.json", "w") as f:
            json.dump(data_to_dump, f, indent=4)
    else:
        print("Not enough trades to process.")


if __name__ == "__main__":
    asyncio.run(main())
