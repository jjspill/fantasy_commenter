import json
import re

import asyncpg
from bs4 import BeautifulSoup

from rankings_service.rankings import Player, RankingsScraper


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
        players = [Player(name=item["player_name"]) for item in data["players"]]
        return players

    async def write_to_db(self, players):
        conn = await asyncpg.connect(
            user="yourusername",
            password="yourpassword",
            database="fantasy_pros",
            host="127.0.0.1",
        )
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS players (
                id serial PRIMARY KEY,
                name text
            )
            """
        )
        for player in players:
            await conn.execute(
                """
                INSERT INTO players(name) VALUES($1)
            """,
                player.name,
            )
        await conn.close()


async def main():
    config = "dynasty-superflex"
    scraper = FantasyProsScraper(configurations[config])
    html = await scraper.fetch_data()
    raw_data = scraper.extract_data(html)
    if raw_data:
        players = scraper.parse_data(raw_data)
        print(players)
        await scraper.write_to_db(players)
