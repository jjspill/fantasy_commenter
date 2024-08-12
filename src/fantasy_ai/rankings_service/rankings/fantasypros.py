import json
import re
from dataclasses import dataclass

import pytz
from bs4 import BeautifulSoup
from google.cloud import firestore

from fantasy_ai.rankings_service.helpers.generic_helpers import get_dates, get_player_id
from fantasy_ai.rankings_service.rankings.rankings import RankingsScraper

db = firestore.Client()


@dataclass
class Fantasypros_Player:
    name: str
    age: int
    position: str
    rank_avg: int
    pos_rank: str
    tier: int


class FantasyProsScraper(RankingsScraper):
    def __init__(self, config_url: str):
        super().__init__(config_url)

    def extract_data(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        script_tags = soup.find_all("script")
        pattern = re.compile(r"var ecrData = ({.*?});", re.S)
        for script in script_tags:
            if script.string:
                match = pattern.search(script.string)
                if match:
                    return match.group(1)
        return None

    def parse_data(self, ecr_data_raw):
        data = json.loads(ecr_data_raw)
        players = [
            Fantasypros_Player(
                name=item["player_name"],
                age=int(item["player_age"]),
                position=item["player_position_id"],
                rank_avg=float(item["rank_ave"]),
                pos_rank=item["pos_rank"],
                tier=item["tier"],
            )
            for item in data["players"]
        ]
        return players

    async def write_to_db(self, players):
        print("Writing to database...")
        batch = db.batch()
        rankings_col_ref = db.collection("rankings")
        current_date, current_time = get_dates()

        for player in players:
            player_id = get_player_id(player.name)
            player_doc_ref = rankings_col_ref.document(player_id)

            fantasypros_player_col_ref = player_doc_ref.collection("fantasypros")
            date_doc_ref = fantasypros_player_col_ref.document(current_date)

            player_data = player.__dict__
            player_data.update({"ranking_date": current_time})

            batch.set(date_doc_ref, player_data)

        batch.commit()

        print("Data written successfully.")
