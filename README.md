## City Weather Competition

This is a weather comparison app for a list of cities, built with FastAPI, Poetry, deployed on Heroku.

### How to get more cities from AccuWeather

Find API key in `.env` on ec2.

```
curl -X GET "http://dataservice.accuweather.com/locations/v1/cities/search?apikey=<api-key>&q=<city name>"
```
