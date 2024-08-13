import asyncio

import typer

from src.config import Mode
from src.sleeper_api_cliient import SleeperAPIClient
from src.utils import write_players_to_json

app = typer.Typer()


@app.command()
def main(
    mode: str = typer.Option(help="Mode of operation, either 'daily' or 'all-time'"),
):
    """
    Executes the data fetching and uploading process based on the specified mode.
    """
    print(f"Running in {mode} mode.")
    if mode.lower() == "daily":
        enum_mode = Mode.DAILY
    elif mode.lower() == "all-time":
        enum_mode = Mode.ALL_TIME
    else:
        raise ValueError("Invalid mode. Please specify either 'daily' or 'all-time")
    asyncio.run(process_sleeper_data(enum_mode))


async def process_sleeper_data(mode: Mode):
    print("Fetching player data...")
    sleeper_client = SleeperAPIClient(mode)
    await sleeper_client.fetch_data()
    print("Writing data to players.json...")
    write_players_to_json(sleeper_client.players)


if __name__ == "__main__":
    app()
