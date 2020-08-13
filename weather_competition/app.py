"""City Weather Competition API"""
import json
import requests
from datetime import datetime, timedelta
from fastapi import FastAPI
from pytz import UTC

from weather_competition.score import score_function
from settings import API_KEY


app = FastAPI()
BASE_URL = "https://api.openweathermap.org/data/2.5/onecall"


"""
Helpers
"""


def _load_city_data():
    with open('./data/city_list.json') as f:
        city_list = json.load(f)
    return {city['id']: city for city in city_list}


CITY_ID_LOOKUP = _load_city_data()


def _get_datetime(day_delta, ref_dt=None):
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


def _get_query_string(city_id, time_opt, day_delta=0):
    data = CITY_ID_LOOKUP[city_id]
    lat = data['coord']['lat']
    lon = data['coord']['lon']
    if time_opt == 'today':
        # This endpoint only has current and forecast, no historical
        # Exclude all except current
        part = "minutely,hourly,daily"
        return (f"?lat={lat}&lon={lon}&exclude={part}&appid={API_KEY}"
                f"&units=imperial")
    if time_opt == 'past':
        dt = _get_datetime(day_delta)
        return (f"/timemachine?lat={lat}&lon={lon}"
                f"&dt={dt}&appid={API_KEY}&units=imperial")


# TODO: score_function to be impl
def _get_scores(responses):
    return [score_function(resp) for resp in responses]


"""
Endpoints
"""


@app.get('/')
def index():
    return 'hello world'


@app.get("/score")
def get_city_score(
    city_id: int, period: str = 'today', day_delta: int = 0
):
    q = _get_query_string(city_id, period, day_delta)
    print(BASE_URL + q)
    resp = requests.get(
        BASE_URL + q,
        headers={"Content-Type": "application/json"}
    )
    timestamp = _get_datetime(0)
    resp_json = resp.json()
    score = score_function(resp_json)
    city_name = CITY_ID_LOOKUP[city_id]['name']
    return {
        'city_id': city_id,
        'city_name': city_name,
        'timestamp': timestamp,
        'weather': resp_json,
        'score': score
    }


# TODO: query should be in a daily scheduled job.
# The job queries the past day's weather for all cities and log to
# DynamoDB which the frontend consumes via this endpoint.
# This endpoint should be re-written to call dynamodb
# and the current code should be moved to that scheduled job.
@app.get("/scores7d")
def get_city_scores(city_id: int, history: bool = False):
    responses = []
    # Per OpenWeatherAPI doc:
    # https://openweathermap.org/api/one-call-api#history
    # Past days queries take one day at a time
    for i in range(1, 2):
        response = get_city_score(city_id, period='past', day_delta=i)
        responses.append(response)
    return responses


@app.get('/cities')
def get_cityids():
    return CITY_ID_LOOKUP
