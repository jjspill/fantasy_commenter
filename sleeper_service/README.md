# Sleeper Service (I guess this should be called fantasy_data_service or something like that because we are not fetching leagues from sleeper here)

## Overview

The sleeper service is responsible for:

- Retrieving a list of players from the Sleeper API, filtering them by a set of rules, and storing them in the database.
- For each player, it retrieves their stats and news from the Sleeper API and stores them in the database.
- There are two ways this can run, either as an database init where all player data for the past 5 years and all news (limit 10) is retrieved and stored in the database, or as a daily update where only the latest news is fetched. Adittioionally, on Tuesdays, the weekly stats for the past week are fetched.

## Running the Service

1. Install poetry if you haven't already. You can do this by running `pip install poetry`.
2. Run `poetry install` to install all dependencies.
3. Run `poetry run python main.py --mode ALL_TIME` to fetch all player data and stats, or `poetry run python main.py --mode DAILY` to fetch the latest news and stats for the past week.

## Organizational Structure

### `main.py`

- A simple file that uses `typer` to read in the `mode` and then calls the `SleeperAPIClient` with the `mode`.

### `sleeper_api_client.py`

- The sleeper API client is the driver class for this service. It inits with the firestore db, the list of sleeper players, and the `mode` (either `ALL_TIME` or `DAILY`).
- The first part of the class is focused on fetching player data, that is `SleeperProfiles`, `SleeperNews`, `SleeperPrevWeekStats`, and `SleeperHistoricalStats`.

- **How data fetching happens**:
    1. Fetch all players from the sleeper API. The response contains 9k+ players so we filter them down in `utils.py/filter_players`. See that function for more details.
    2. Then for each player that passes the filter, we asynchronously call `_create_player` which fetches the players news and stats.
        1. `_fetch_player_news` functions by using the sleeper GraphQL API to fetch the latest news for a player. The `mode` is used to determine if we are fetching all news or just the news from the past 24 hours.
        2. There are two function for fetching stats. `_fetch_player_prev_week_stats` and `_fetch_player_historical_stats`. The first fetches the stats for the past week, and the second fetches the stats for the past 5 years. The `mode` is used to determine which function to call.
    3. For now, after all fetching happens data is written to a JSON file. This will need to be changed to write to the database. For now this is fine as the historical data will only need to be fetched once.

### `utils.py`

- Utils contains a few helper functions that are mainly focused on filtering data, and extracting data from the sleeper API response.

### `types.py`

- Types contains the data classes that are used to store the data that is fetched from the sleeper API.

### `config.py`

- A very small file for storing all of the constants that are used in the sleeper service.
