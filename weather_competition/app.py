"""City Weather Competition API"""
import json
import requests
from datetime import datetime, timedelta
from fastapi import FastAPI
from pytz import UTC

from weather_competition.score import score_func  # , avg_score
from settings import API_KEY


app = FastAPI()
BASE_URL = "http://dataservice.accuweather.com/currentconditions/v1/"


"""
Helpers
"""


def _load_city_data():
    with open('./data/city_list.json') as f:
        city_list = json.load(f)
    return {city['Key']: city for city in city_list}


CITY_ID_LOOKUP = _load_city_data()


def _get_utc_midnight_epoch(day_delta, ref_dt=None):
    """
    Returns midnight time of a day in epoch second in UTC
    day_delta is an integer from 0 to 6. 0 means today, 1 means yesterday, etc.
    """
    if not ref_dt:
        ref_dt = datetime.now()
    dt_ago = ref_dt - timedelta(days=day_delta)
    # UTC midnight
    dt_ago_midnight = dt_ago.replace(
        hour=0, minute=0, second=0, microsecond=0, tzinfo=UTC
    )
    return int(dt_ago_midnight.timestamp())


def _get_score_item(city_id, city_name, timestamp, weather):
    return {
        'city_id': city_id,
        'city_name': city_name,
        'timestamp': timestamp,
        'weather': weather,
        'score': score_func(weather)
    }


"""
Endpoints
"""


@app.get('/')
def index():
    return 'hello world'


@app.get("/now")
def get_city_score(city_id: int, period: str = 'now'):
    city_name = CITY_ID_LOOKUP[str(city_id)]['EnglishName']
    q = BASE_URL + f"{city_id}?apikey={API_KEY}&details=true"
    resp = requests.get(q, headers={"Content-Type": "application/json"})
    weather = resp.json()[0]
    return _get_score_item(
        city_id, city_name, timestamp=_get_utc_midnight_epoch(0),
        weather=weather)


# TODO: query should be in a daily scheduled job after utc midnight.
# The job queries the past day's weather for all cities and log to
# DynamoDB which the frontend consumes via this endpoint.
# This endpoint should be re-written to call dynamodb
# and the current code should be moved to that scheduled job.
@app.get("/last24h")
def get_city_scores(city_id: int):
    timestamp = _get_utc_midnight_epoch(0)
    city_name = CITY_ID_LOOKUP[str(city_id)]['EnglishName']
    q = BASE_URL + f"{city_id}/historical/24?apikey={API_KEY}&details=true"
    resp = requests.get(q, headers={"Content-Type": "application/json"})
    data = resp.json()
    return [
        _get_score_item(city_id, city_name, timestamp, weather)
        for weather in data
    ]


@app.get('/cities')
def get_cityids():
    return CITY_ID_LOOKUP
