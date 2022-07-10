## City Weather Competition

This is a weather comparison app for a list of cities, built with FastAPI, Poetry, deployed on Heroku.

### How to get more cities from AccuWeather

Find API key in `.env` on ec2.

```
curl -X GET "http://dataservice.accuweather.com/locations/v1/cities/search?apikey=<api-key>&q=<city name>"
```

### How to deploy

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
