from datetime import datetime
from nose.tools import eq_
from daf_fruit_dist.iso_time import ISOTime
from mock import Mock


now_mock = Mock()
now_mock.return_value = datetime(2013, 4, 11, 11, 10, 46, 302000)


def _create_time_mock(daylight_savings):
    time_mock = Mock()
    time_mock.altzone = 82800   # +23 hours
    time_mock.timezone = 79200  # +22 hours
    time_mock.daylight = daylight_savings
    return time_mock


def test_daylight_savings_on():
    expected_result = '2013-04-11T11:10:46.302-2300'
    time_mock = _create_time_mock(daylight_savings=True)
    actual_result = ISOTime.now(now_fn=now_mock, time=time_mock).as_str
    eq_(actual_result, expected_result)


def test_daylight_savings_off():
    expected_result = '2013-04-11T11:10:46.302-2200'
    time_mock = _create_time_mock(daylight_savings=False)
    actual_result = ISOTime.now(now_fn=now_mock, time=time_mock).as_str
    eq_(actual_result, expected_result)
