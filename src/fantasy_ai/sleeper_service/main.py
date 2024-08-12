import asyncio

from fantasy_ai.sleeper_service.helpers.data_helpers import (
    build_player_map,
    fetch_player_data,
    upload_sleeper_data,
)


async def main():
    print("Fetching player data...")
    player_data = await fetch_player_data()
    print("Uploading player data to database...")
    # await upload_sleeper_data(player_data)
    print("Player data uploaded.")
    build_player_map(player_data)
    print("Player map built.")


if __name__ == "__main__":
    asyncio.run(main())