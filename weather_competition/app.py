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
    part = "minutely"
    if time_opt == 'today':
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


@app.get("/weatherscores")
def get_weather_scores(city_id: int):
    responses = {}
    q_today = _get_query_string(city_id, 'today')
    resp_today = requests.get(
        BASE_URL + q_today,
        headers={"Content-Type": "application/json"}
    )
    # Per OpenWeatherAPI doc:
    # https://openweathermap.org/api/one-call-api#history
    # Past days queries take one day at a time
    responses[_get_datetime(0)] = resp_today.json()
    for i in range(1, 6):
        q_past = _get_query_string(city_id, 'past', day_delta=i)
        print(BASE_URL + q_past)
        resp = requests.get(
            BASE_URL + q_past,
            headers={"Content-Type": "application/json"}
        )
        responses[_get_datetime(i)] = resp.json()

    scores = _get_scores(responses)
    return {
        'weather': responses,
        'score': scores
    }


@app.get('/cities')
def get_cityids():
    return CITY_ID_LOOKUP
