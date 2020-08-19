from datetime import datetime
from weather_competition import __version__, score, utils
from tests.constants import ACCU_WEATHER_DATA, SCORES_LIST


def test_version():
    assert __version__ == "0.1.0"


def test_get_utc_midnight_epoch():
    dt = datetime(2020, 8, 10, 18, 30, 44, 493161)
    assert utils.get_utc_midnight_epoch(0, ref_dt=dt) == 1597017600
    assert utils.get_utc_midnight_epoch(1, ref_dt=dt) == 1596931200
    assert utils.get_utc_midnight_epoch(2, ref_dt=dt) == 1596844800


def test_score_func():
    res_score, desc = score.score_func(ACCU_WEATHER_DATA)
    assert res_score == 53.0
    assert desc['hot']
    assert not desc['cold']
    assert desc['humid']
    assert not desc['dry']
    assert desc['cloudy']
    assert desc['rainy']


def test_summarize_desc():
    expected = {
        'hot': True,
        'cold': False,
        'humid': True,
        'dry': False,
        'cloudy': True,
        'rainy': False
    }
    actual = score.summarize_desc(SCORES_LIST)
    assert actual == expected
