"""
Scheduled job to populate DynamoDB, run daily after utc midnight
To run:
nohup python -m weather_competition.scheduled_job &
"""

import sys
import requests

import boto3
from datetime import datetime
from time import sleep
from apscheduler.schedulers.blocking import BlockingScheduler

from weather_competition.utils import get_utc_midnight_epoch, CITY_ID_LOOKUP
from settings import API_KEY, BASE_URL, AWS_ACCESS_KEY_ID, \
    AWS_SECRET_ACCESS_KEY, AWS_REGION


TEST_CITY_IDS = ["349727", "351409"]

sys.path.append(".")
session = boto3.session.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)
db = session.resource('dynamodb')
weather_table = db.Table('dragonbot_weather')

sched = BlockingScheduler()


def query_api_insert_db(city_id):
    day_start_at = get_utc_midnight_epoch(0)
    city_name = CITY_ID_LOOKUP[str(city_id)]["EnglishName"]
    q = BASE_URL + f"{city_id}/historical/24?apikey={API_KEY}&details=true"
    resp = requests.get(q, headers={"Content-Type": "application/json"})
    data = resp.json()
    for weather in data:
        datum = {
            "city_id": city_id,
            "city_name": city_name,
            "day_start_at": day_start_at,
            "inserted_at": int(datetime.now().timestamp()*1000),
            "weather": weather
        }
        weather_table.put_item(Item=datum)


# This runs daily at UTC00:02, ET20:02
@sched.scheduled_job("cron", hour=0, minute=2, timezone="UTC")
def insert_weather_last24h():
    print("Scheduled job: executing...")
    for city_id in TEST_CITY_IDS:
        try:
            query_api_insert_db(city_id)
            sleep(5)
            print(f"Scheduled db insert executed at {datetime.now()}")
        except Exception as e:
            print(f"Scheduled db insert failed for city {city_id}: {e}")


print("Scheduled job: started...")
sched.start()
