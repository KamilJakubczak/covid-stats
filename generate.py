import requests
import json

from datetime import datetime
from database import init_db, db_session
from models import Run


def get_data():
    return requests.get('https://corona.lmao.ninja/v3/covid-19/countries')


def json_str_to_dict(json_str: str) -> dict:
    return json.loads(json_str)


def count_countries(payload: dict) -> int:
    return len(payload)


def check_if_key_is_taken(dict_to_check: dict, key_name: str) -> bool:
    if key_name in dict_to_check.keys():
        raise KeyError(f'The key name - {key_name} - is already taken')


def count_daily_abs_increase(payload: dict) -> dict:
    #  return { for country in payload }
    print({country['country']: country['todayCases'] for country in payload})


def get_top_countries(dict_data: dict, count: int = None) -> list:
    sorted_data = sorted(
        dict_data,
        key=lambda country: country['todayCases'],
        reverse=True)
    if count:
        return {country['country']: country['todayCases'] for country in sorted_data[0:count]}

    return {country['country']: country['todayCases'] for country in sorted_data}


def log_run_in_db() -> None:

    current_run = Run('Kamil')
    db_session.add(current_run)
    db_session.commit()


def run() -> None:
    init_db()
    request_data = get_data()
    dict_data = json_str_to_dict(request_data.text)
    country_count = count_countries(dict_data)
    #  check_if_key_is_taken(dict_data[0], 'tests')
    #  count_daily_abs_increase(dict_data)

    log_run_in_db()

if __name__ == '__main__':
    run()
