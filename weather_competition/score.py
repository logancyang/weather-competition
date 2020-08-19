"""
Calculate a score based on weather info.

A sample weather object from AccuWeather API:
{
    "EpochTime": 1597326180,
    "WeatherText": "Rain",
    "WeatherIcon": 18,
    "HasPrecipitation": True,
    "PrecipitationType": "Rain",
    "IsDayTime": True,
    "Temperature": {
        "Metric": {
            "Value": 25.0,
            "Unit": "C",
            "UnitType": 17
        },
        "Imperial": {
            "Value": 77.0,
            "Unit": "F",
            "UnitType": 18
        }
    },
    "RealFeelTemperature": {
        "Metric": {
            "Value": 28.2,
            "Unit": "C",
            "UnitType": 17
        },
        "Imperial": {
            "Value": 83.0,
            "Unit": "F",
            "UnitType": 18
        }
    },
    "RelativeHumidity": 68,
    "WindGust": {
        "Speed": {
            "Metric": {
                "Value": 6.1,
                "Unit": "km/h",
                "UnitType": 7
            },
            "Imperial": {
                "Value": 3.8,
                "Unit": "mi/h",
                "UnitType": 9
            }
        }
    },
    "UVIndex": 1,
    "UVIndexText": "Low",
    "Visibility": {
        "Metric": {
            "Value": 16.1,
            "Unit": "km",
            "UnitType": 6
        },
        "Imperial": {
            "Value": 10.0,
            "Unit": "mi",
            "UnitType": 2
        }
    },
    "CloudCover": 100,
    "TemperatureSummary": {
        "Past24HourRange": {
            "Minimum": {
                "Metric": {
                    "Value": 22.2,
                    "Unit": "C",
                    "UnitType": 17
                },
                "Imperial": {
                    "Value": 72.0,
                    "Unit": "F",
                    "UnitType": 18
                }
            },
            "Maximum": {
                "Metric": {
                    "Value": 32.2,
                    "Unit": "C",
                    "UnitType": 17
                },
                "Imperial": {
                    "Value": 90.0,
                    "Unit": "F",
                    "UnitType": 18
                }
            }
        }
    }
}

V0 scoring formula:
    score = 100 - abs(T - [range]) - abs(H - [range]) * 0.5
            - I(clouds>=90) * 5 - I(HasPrecipitation) * 20

T: RealFeelTemperature. [range]: 62-79
H: RelativeHumidity. [range]: 35-50
I(CloudCover>=90): whether CloudCover >= 90, if yes, -5
I(HasPrecipitation): whether there is any precipitation, if yes, -20
"""


T_UPPER = 79
T_LOWER = 62
H_UPPER = 50
H_LOWER = 35
HUMID_PENALTY_MULT = 1
PRECIP_PENALTY = 20


def score_func(weather):
    """weather passed in is assumed to be hourly"""
    temp = weather['RealFeelTemperature']['Imperial']['Value']
    temp_penalty = 0
    descriptions = {
        'hot': False,
        'cold': False,
        'humid': False,
        'dry': False,
        'cloudy': False,
        'rainy': False
    }
    if temp < T_LOWER:
        temp_penalty = T_LOWER - temp
        descriptions['cold'] = True
    elif temp > T_UPPER:
        temp_penalty = temp - T_UPPER
        descriptions['hot'] = True
    humid = weather['RelativeHumidity']
    humid_penalty = 0
    if humid < H_LOWER:
        humid_penalty = (H_LOWER - humid) * HUMID_PENALTY_MULT
        descriptions['dry'] = True
    elif humid > H_UPPER:
        humid_penalty = (humid - H_UPPER) * HUMID_PENALTY_MULT
        descriptions['humid'] = True

    cloud_penalty = 0
    if weather['CloudCover'] >= 90:
        cloud_penalty = 5
        descriptions['cloudy'] = True

    precip_penalty = 0
    if weather['HasPrecipitation']:
        precip_penalty = PRECIP_PENALTY
        descriptions['rainy'] = True

    return 100 - temp_penalty - humid_penalty -\
        cloud_penalty - precip_penalty, descriptions


def _summarize(desc_list, prop, threshold=2):
    """Returns the count of properties such as hot, cold, dry, humid,
    cloudy, rainy, and whether they exceed a threshold
    """
    count = [desc[prop] for desc in desc_list].count(True)
    return count, count > threshold


def summarize_desc(city_scores):
    """Takes in a list of score tuples (with description dictionary)
    and returns a summary description"""
    city_descs = [tup[2] for tup in city_scores]
    summary = {
        'hot': False,
        'cold': False,
        'humid': False,
        'dry': False,
        'cloudy': False,
        'rainy': False
    }
    num_hot, summary['hot'] = _summarize(city_descs, 'hot')
    num_cold, summary['cold'] = _summarize(city_descs, 'cold')
    num_humid, summary['humid'] = _summarize(city_descs, 'humid')
    num_dry, summary['dry'] = _summarize(city_descs, 'dry')
    num_cloudy, summary['cloudy'] = _summarize(
        city_descs, 'cloudy', threshold=3
    )
    num_rainy, summary['rainy'] = _summarize(city_descs, 'rainy')
    return summary
