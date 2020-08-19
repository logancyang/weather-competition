"""City Weather Competition API"""
import json
import requests
from functools import partial

from boto3.dynamodb.conditions import Key
from fastapi import FastAPI

from weather_competition.score import score_func, summarize_desc
from weather_competition.utils import CITY_ID_LOOKUP, get_utc_midnight_epoch,\
    create_db_session
from settings import API_KEY, BASE_URL, DRAGON_API_KEY


app = FastAPI()
_, weather_table = create_db_session()
DAY_INTERVAL = 86400 - 2


"""Helpers"""


def _add_score(datum, details=False):
    datum['score'], datum['desc'] = score_func(datum['weather'])
    if details:
        return datum
    return datum['for_epoch'], datum['score'], datum['desc']


def _transform_weather_json(data):
    for item in data:
        item['weather'] = json.loads(item['weather'])
    return data


def _query_city(city_id, num_past_days, table=None):
    if not table:
        _, table = create_db_session()
    # TODO: could be using the local midnight to query for_epoch range
    day_start_at = get_utc_midnight_epoch(num_past_days)
    resp = table.query(
        KeyConditionExpression=Key('city_id').eq(city_id) &
        Key('for_epoch').between(
            day_start_at, day_start_at + num_past_days * DAY_INTERVAL - 2
        )
    )
    return _transform_weather_json(resp['Items'])


def _get_city_scores(
    num_past_days: int, city_id: int, apikey: str, details: bool = False
):
    if apikey != DRAGON_API_KEY:
        return "403 Forbidden"
    data = _query_city(str(city_id), num_past_days, table=weather_table)
    return [_add_score(datum, details) for datum in data]


_get_city_scores_24h = partial(_get_city_scores, 1)
_get_city_scores_7d = partial(_get_city_scores, 8)


"""Endpoints"""


@app.get('/')
def index():
    return 'hello world'


# Note: DO NOT expose this endpoint to app, free AccuWeather API only
# allows 50 requests per day
@app.get("/now")
def get_city_score(city_id: int, apikey: str, period: str = 'now'):
    if apikey != DRAGON_API_KEY:
        return "403 Forbidden"
    city_name = CITY_ID_LOOKUP[str(city_id)]['EnglishName']
    q = BASE_URL + f"{city_id}?apikey={API_KEY}&details=true"
    resp = requests.get(q, headers={"Content-Type": "application/json"})
    weather = resp.json()[0]
    datum = {
        'city_id': city_id,
        'city_name': city_name,
        'day_start_at': get_utc_midnight_epoch(0),
        'weather': weather
    }
    return _add_score(datum)


@app.get("/last24h")
def get_scores_24h(city_id: int, apikey: str, details: bool = False):
    return _get_city_scores_24h(city_id, apikey, details)


@app.get("/last7d")
def get_scores_7d(city_id: int, apikey: str, details: bool = False):
    return _get_city_scores_7d(city_id, apikey, details)


@app.get("/compete24h")
def get_winner_24h(city_ids: str, apikey: str):
    if apikey != DRAGON_API_KEY:
        return "403 Forbidden"
    scores = []
    city_id_list = [id_str for id_str in city_ids.split(",")]
    for city_id in city_id_list:
        city_24h_tups = _get_city_scores_24h(int(city_id), apikey)
        if not city_24h_tups:
            continue
        city_24h_scores = [tup[1] for tup in city_24h_tups]
        avg_score = sum(city_24h_scores) / len(city_24h_scores)
        summary_24h_desc = summarize_desc(city_24h_tups)
        city_name = CITY_ID_LOOKUP[str(city_id)]['EnglishName']
        scores.append((city_name, avg_score, summary_24h_desc))
    return sorted(scores, key=lambda tup: tup[1], reverse=True)


@app.get('/cities')
def get_cityids(apikey: str):
    if apikey != DRAGON_API_KEY:
        return "403 Forbidden"
    return CITY_ID_LOOKUP
