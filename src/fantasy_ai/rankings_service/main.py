import asyncio

from rankings.fantasypros import FantasyProsScraper

configurations = {
    "dynasty-superflex": "https://www.fantasypros.com/nfl/rankings/dynasty-superflex.php",
    "dynasty-1qb": "https://www.fantasypros.com/nfl/rankings/dynasty-overall.php",
    "redraft-ppr": "https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php",
}


async def main():
    configs = ["dynasty-superflex", "dynasty-1qb", "redraft-ppr"]
    for config in configs:
        print(f"Fetching data for {config}...")
        scraper = FantasyProsScraper(configurations[config])
        html = await scraper.fetch_data()
        raw_data = scraper.extract_data(html)
        if raw_data:
            players = scraper.parse_data(raw_data)
            await scraper.write_to_db(players, config)
            print("Data written to database.")


if __name__ == "__main__":
    asyncio.run(main())
