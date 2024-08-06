import json
import re
from dataclasses import dataclass

import asyncpg
from bs4 import BeautifulSoup
from rankings import RankingsScraper


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
        conn = await asyncpg.connect(
            user="postgres",
            password="mypassword",
            database="mydatabase",
            host="127.0.0.1",
        )

        await conn.execute(
            """
            DROP TABLE IF EXISTS fantasy_pros
            """
        )

        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fantasy_pros (
                id serial PRIMARY KEY,
                name text,
                age int,
                position text,
                rank_avg float,
                pos_rank text,
                tier int
            )
            """
        )
        for player in players:
            await conn.execute(
                """
                INSERT INTO fantasy_pros(name, age, position, rank_avg, pos_rank, tier)
                VALUES($1, $2, $3, $4, $5, $6)
                """,
                player.name,
                player.age,
                player.position,
                player.rank_avg,
                player.pos_rank,
                player.tier,
            )
        await conn.close()
