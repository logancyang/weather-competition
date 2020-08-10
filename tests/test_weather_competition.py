from datetime import datetime
from weather_competition import __version__, app


def test_version():
    assert __version__ == '0.1.0'


def test__get_datetime():
    dt = datetime(2020, 8, 10, 18, 30, 44, 493161)
    assert app._get_datetime(0, ref_dt=dt) == 1597017600
    assert app._get_datetime(1, ref_dt=dt) == 1596931200
    assert app._get_datetime(2, ref_dt=dt) == 1596844800
