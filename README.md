## City Weather Competition

This is a weather comparison app for a list of cities, built with FastAPI, Poetry, deployed on Heroku.

### How to get more cities from AccuWeather

Find API key in `.env` on ec2.

```
curl -X GET "http://dataservice.accuweather.com/locations/v1/cities/search?apikey=<api-key>&q=<city name>"
```

### How to deploy: EC2 for scheduled jobs

ssh into ec2 and go to the repo, 

```
# Start the python environment
poetry shell
# Find the running processes
ps -ef | grep python
# Kill the existing ones
kill -9 <pid>
# Start new ones
nohup python -u -m weather_competition.scheduled_job &
nohup python -u scheduled_email/send_email.py &> emaillog.out & 
```

### How to deploy: Heroku for backend service

Go to Heroku https://dashboard.heroku.com/apps/dragon-weather/deploy/github, make sure to manually deploy master branch.

### How to test Heroku deploy

```
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X GET https://dragon-weather.herokuapp.com/compete24h\?apikey\=<api-key>\&city_ids\=348181
```
