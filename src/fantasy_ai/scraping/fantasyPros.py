import asyncio
import json
import re
from dataclasses import dataclass

import aiohttp
import asyncpg
from bs4 import BeautifulSoup


@dataclass
class Player:
    name: str


configurations = {
    "dynasty-superflex": "https://www.fantasypros.com/nfl/rankings/dynasty-superflex.php",
}


async def get_fantasy_pros_rankings(config: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(configurations[config]) as response:
            return await response.text()


def extract_ecr_data(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    script_tags = soup.find_all("script")

    # Pattern to match the ecrData object
    pattern = re.compile(r"var ecrData = ({.*?});", re.S)

    for script in script_tags:
        if script.string:
            match = pattern.search(script.string)
            if match:
                ecr_data_raw = match.group(1)
                return ecr_data_raw

    return None


def parse_ecr_data(ecr_data_raw):
    # Convert the JSON string into Python objects
    data = json.loads(ecr_data_raw)

    players = [Player(name=item["player_name"]) for item in data["players"]]
    return players


async def write_to_db(players):
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
    html = await get_fantasy_pros_rankings(config)
    ecr_data = extract_ecr_data(html)
    if ecr_data:
        open("ecrData.json", "w").write(ecr_data)
        players = parse_ecr_data(ecr_data)
        print(players)


if __name__ == "__main__":

    asyncio.run(main())
