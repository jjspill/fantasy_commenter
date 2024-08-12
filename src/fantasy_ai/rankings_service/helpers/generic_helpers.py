from datetime import datetime

import pytz


def get_dates() -> list:
    eastern = pytz.timezone("US/Eastern")
    now_est = datetime.now(eastern)
    formatted_date = now_est.strftime("%Y-%m-%d")
    formatted_date_time = now_est.isoformat()
    return [formatted_date, formatted_date_time]


def get_player_id(player_name: str) -> str:
    return player_name[0].lower() + player_name.split(" ")[-1].lower()
