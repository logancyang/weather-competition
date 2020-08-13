"""
Calculate a score based on weather info.
For a list of possible weather conditions, check the link below
https://openweathermap.org/weather-conditions
Any weather code that doesn't start with 8 results in
a decrease in score.

A sample weather object:
{
    "dt": 1597068000,
    "temp": 77.4,
    "feels_like": 83.32,
    "pressure": 1014,
    "humidity": 83,
    "dew_point": 71.83,
    "clouds": 90,
    "visibility": 9656,
    "wind_speed": 4.7,
    "wind_deg": 0,
    "weather": [
        {
            "id": 211,
            "main": "Thunderstorm",
            "description": "thunderstorm",
            "icon": "11d"
        },
        {
            "id": 500,
            "main": "Rain",
            "description": "light rain",
            "icon": "10d"
        }
    ]
}

V0 scoring formula:
    score = 100 - abs(T - [range]) - abs(H - [range]) * 0.5
            - I(clouds>=90) * 5 - I(Not8xx) * 20

T: feels_like. [range]: 62-76
H: humidity. [range]: 35-50
I(clouds>=90): whether clouds >= 90, if yes, -5
I(Not8xx): whether there is any weather code not starting with 8, if yes, -20
"""


T_UPPER = 76
T_LOWER = 62
H_UPPER = 50
H_LOWER = 35
HUMID_PENALTY_MULT = 0.5
CONDITION_PENALTY = 20


def score_function(weather):
    temp = weather['feels_like']
    temp_penalty = 0
    if temp < T_LOWER:
        temp_penalty = T_LOWER - temp
    elif temp > T_UPPER:
        temp_penalty = temp - T_UPPER
    humid = weather['humidity']
    humid_penalty = 0
    if humid < H_LOWER:
        humid_penalty = (H_LOWER - humid) * HUMID_PENALTY_MULT
    elif humid > H_UPPER:
        humid_penalty = (humid - H_UPPER) * HUMID_PENALTY_MULT
    cloud_penalty = 1 if weather['clouds'] >= 90 else 0
    condition_set = set([str(item['id']) for item in weather['weather']])
    condition_penalty = CONDITION_PENALTY if \
        any(not code.startswith('8') for code in condition_set) else 0
    return 100 - temp_penalty - humid_penalty -\
        cloud_penalty - condition_penalty
