from datetime import datetime
from weather_competition import __version__, score, utils


ACCU_WEATHER_DATA = {
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


def test_version():
    assert __version__ == "0.1.0"


def test_get_utc_midnight_epoch():
    dt = datetime(2020, 8, 10, 18, 30, 44, 493161)
    assert utils.get_utc_midnight_epoch(0, ref_dt=dt) == 1597017600
    assert utils.get_utc_midnight_epoch(1, ref_dt=dt) == 1596931200
    assert utils.get_utc_midnight_epoch(2, ref_dt=dt) == 1596844800


def test_score_func():
    assert score.score_func(ACCU_WEATHER_DATA) == 62.0
