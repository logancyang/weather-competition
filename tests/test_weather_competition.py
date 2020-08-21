from datetime import datetime
from pytest import approx

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
    assert desc['hot']
    assert not desc['cold']
    assert desc['humid']
    assert not desc['dry']
    assert desc['cloudy']
    assert desc['rainy']


def test__summarize():
    city_descs = [tup[2] for tup in SCORES_LIST]
    assert score._summarize(city_descs, 'hot') == (7, True)
    assert score._summarize(city_descs, 'cold') == (0, False)
    assert score._summarize(city_descs, 'humid') == (16, True)
    assert score._summarize(city_descs, 'dry') == (2, False)
    assert score._summarize(city_descs, 'cloudy') == (0, False)
    assert score._summarize(city_descs, 'rainy') == (0, False)


def test__summary_stats():
    city_descs = [tup[2] for tup in SCORES_LIST]
    assert score._summary_stats(city_descs, 'temperature') ==\
        approx((84.0, 73.458333, 63.0))
    assert score._summary_stats(city_descs, 'humidity') ==\
        approx((77, 58.958333, 26))


def test_summarize_desc():
    expected = {
        'hot': True,
        'cold': False,
        'humid': True,
        'dry': False,
        'cloudy': False,
        'rainy': False,
        'avg_humid': approx(58.9583),
        'avg_temp': approx(73.4583),
        'max_humid': 77,
        'max_temp': 84,
        'min_humid': 26,
        'min_temp': 63
    }
    actual = score.summarize_desc(SCORES_LIST)
    assert actual == expected
