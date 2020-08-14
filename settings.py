import os
from dotenv import load_dotenv

load_dotenv('.env')

API_KEY = os.environ.get('API_KEY')
BASE_URL = os.environ.get('BASE_URL')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.environ.get('AWS_REGION')
DRAGON_API_KEY = os.environ.get('DRAGON_API_KEY')
DRAGONBOT_URL = os.environ.get('DRAGONBOT_URL')
