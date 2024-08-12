import asyncio

from rankings.fantasypros import FantasyProsScraper

configurations = {
    "dynasty-superflex": "https://www.fantasypros.com/nfl/rankings/dynasty-superflex.php",
}


async def main():
    config = "dynasty-superflex"
    print(f"Fetching data for {config}...")
    scraper = FantasyProsScraper(configurations[config])
    html = await scraper.fetch_data()
    raw_data = scraper.extract_data(html)
    if raw_data:
        players = scraper.parse_data(raw_data)
        await scraper.write_to_db(players)
        print("Data written to database.")


if __name__ == "__main__":
    asyncio.run(main())
