from datetime import datetime
from weather_competition import __version__, app, score


def test_version():
    assert __version__ == "0.1.0"


def test__get_datetime():
    dt = datetime(2020, 8, 10, 18, 30, 44, 493161)
    assert app._get_datetime(0, ref_dt=dt) == 1597017600
    assert app._get_datetime(1, ref_dt=dt) == 1596931200
    assert app._get_datetime(2, ref_dt=dt) == 1596844800


def test_score_function():
    weather_data = {
        "dt": 1597172400,
        "temp": 87.06,
        "feels_like": 88.56,
        "pressure": 1011,
        "humidity": 54,
        "dew_point": 68.41,
        "clouds": 1,
        "visibility": 10000,
        "wind_speed": 9.46,
        "wind_deg": 226,
        "weather": [
            {"id": 500, "main": "Rain",
             "description": "light rain", "icon": "10d"}
        ],
        "pop": 0.6,
        "rain": {"1h": 0.19},
    }
    assert score.score_function(weather_data) == 65.44
