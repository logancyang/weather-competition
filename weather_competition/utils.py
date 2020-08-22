import json
import pytz
import boto3

from datetime import datetime, timedelta
from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION


def load_city_data():
    with open('./data/city_list.json') as f:
        city_list = json.load(f)
    return {city['Key']: city for city in city_list}


CITY_ID_LOOKUP = load_city_data()


def epoch2datestr(epoch, timezone_str):
    tz = pytz.timezone(timezone_str)
    return str(datetime.fromtimestamp(epoch, tz))


def get_midnight_epoch(day_delta, timezone_str, ref_dt=None):
    """
    Returns midnight time of a day in epoch second in name-specified timezone.
    day_delta is an integer from 0 to 6. 0 means today, 1 means yesterday, etc.
    """
    if not ref_dt:
        ref_dt = datetime.now()
    dt_ago = ref_dt - timedelta(days=day_delta)
    tz = pytz.timezone(timezone_str)
    dt_ago_local = tz.localize(dt_ago)
    dt_ago_local_midnight = dt_ago_local.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return int(dt_ago_local_midnight.timestamp()), str(dt_ago_local_midnight)


def create_db_session():
    session = boto3.session.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    db = session.resource('dynamodb')
    weather_table = db.Table('dragonbot_weather_v1')
    return db, weather_table
