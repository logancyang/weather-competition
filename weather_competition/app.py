"""City Weather Competition API"""
import requests
from fastapi import FastAPI

from weather_competition.score import score_func
from weather_competition.utils import CITY_ID_LOOKUP, get_utc_midnight_epoch
from settings import API_KEY, BASE_URL


app = FastAPI()


"""
Helpers
"""


def _get_score_item(city_id, city_name, day_start_at, weather):
    return {
        'city_id': city_id,
        'city_name': city_name,
        'day_start_at': day_start_at,
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
        city_id, city_name, day_start_at=get_utc_midnight_epoch(0),
        weather=weather)


# TODO: query should be in a daily scheduled job after utc midnight.
# The job queries the past day's weather for all cities and log to
# DynamoDB which the frontend consumes via this endpoint.
# This endpoint should be re-written to call dynamodb
# and the current code should be moved to that scheduled job.
@app.get("/last24h")
def get_city_scores(city_id: int):
    day_start_at = get_utc_midnight_epoch(0)
    city_name = CITY_ID_LOOKUP[str(city_id)]['EnglishName']
    q = BASE_URL + f"{city_id}/historical/24?apikey={API_KEY}&details=true"
    resp = requests.get(q, headers={"Content-Type": "application/json"})
    data = resp.json()
    return [
        _get_score_item(city_id, city_name, day_start_at, weather)
        for weather in data
    ]


@app.get('/cities')
def get_cityids():
    return CITY_ID_LOOKUP
