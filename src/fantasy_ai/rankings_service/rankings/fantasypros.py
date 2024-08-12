import json
import re
from dataclasses import dataclass

import pytz
import requests
from bs4 import BeautifulSoup
from google.cloud import firestore

from fantasy_ai.rankings_service.helpers.generic_helpers import get_dates, get_player_id
from fantasy_ai.rankings_service.rankings.rankings import RankingsScraper

db = firestore.Client()


@dataclass
class Fantasypros_Player:
    name: str
    short_name: str
    # team: str
    position: str
    rank_avg: int
    pos_rank: str
    tier: int
    sportsdata_id: str


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
                short_name=item["player_short_name"],
                position=item["player_position_id"],
                rank_avg=float(item["rank_ave"]),
                pos_rank=item["pos_rank"],
                tier=item["tier"],
                sportsdata_id=item["sportsdata_id"],
                # team=item["player_team_id"],
            )
            for item in data["players"]
        ]

        return players

    async def write_to_db(self, players, config_slug):
        print("Writing to database...")
        batch = db.batch()
        rankings_col_ref = db.collection("player_info")
        current_date, current_time = get_dates()

        for player in players:
            # player_id = get_player_id(player.short_name)
            player_doc_ref = rankings_col_ref.document(player.sportsdata_id)
            fantasypros_doc_ref = player_doc_ref.collection("rankings").document(
                "fantasypros-" + config_slug
            )

            new_player_data = player.__dict__
            new_player_data["date"] = current_date
            batch.set(
                fantasypros_doc_ref,
                {"rankings_data": firestore.ArrayUnion([new_player_data])},
                merge=True,
            )

        batch.commit()
        print("Data written successfully.")

    # async def write_to_db(self, players, config_slug):
    #     with open("player_context.py", "w") as f:
    #         f.write('player_context = """\n')
    #         for player in players:
    #             f.write(f"{player.name}, {player.team} {player.position}\n")
    #         f.write('"""')
