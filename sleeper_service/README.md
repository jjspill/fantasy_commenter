# Sleeper Service

## Overview

The sleeper service is responsible for:

- Retrieving a list of players from the Sleeper API, filtering them by a set of rules, and storing them in the database.
- For each player, it retrieves their stats and news from the Sleeper API and stores them in the database.
- There are two ways this can run, either as an database init where all player data for the past 5 years and all news (limit 10) is retrieved and stored in the database, or as a daily update where only the latest news and stats are retrieved and stored in the database.
