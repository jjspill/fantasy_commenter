# Fantasy AI

## Structural Overview

### Leagues Service

This service is responsible for fetching sleeper league and team data. In my head this runs once a day and updates the database with the latest data. However, this might change depending on when we give ai "commentations" on the league. Before giving a commentation, we need to make sure the data is up to date...

### News Service

This is the service that will parse the rss file for links and then scrape the links for the actual news and have AI generate a commentation on the news. This will be stored in the player_info table in the database. Have to figure out a way to map the player name to the sleeper player id.

### Rankings Service

This service is responsible for fetching the latest rankings from fantasypros and storing them in the database. This will be used to generate the rankings for the AI commentations. Also have to figure out here how to map the player name to the sleeper player id.

### Sleeper Service

This service is responsible for fetching the latest sleeper data regarding nfl players and news and storing it in the database. This will be used to generate the AI commentations on the league. Lots of sleeper data to go through and there is no readme because sleeper's GraphQL api is not public but some endpoints not authenticated.

### Trades Service

This service is responsible for detecting trades in the sleeper league, connecting the players and picks in the trade to the data we have in the database and then providing all of that to the AI to generate commentation on the trade. The commentation will need to go in the database under the leagues table and be sent to the user.
