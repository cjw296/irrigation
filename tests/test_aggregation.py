from pandas import DatetimeIndex as I, DataFrame
from pandas._testing import assert_frame_equal

from data import daily_from_hourly


class TestDailyFromHourly:

    def test_max_min(self):
        source = DataFrame(
            {'foo_max': [1, 2, 3],
             'foo_min': [4, 5, 6],
             'other': [7, 8, 9]},
            index=I(['2021-07-05 10:00:00', '2021-07-05 11:00:00', '2021-07-06 12:00:00'])
        )
        expected = DataFrame(
            {'foo_max': [2, 3],
             'foo_min': [4, 6]},
            index=I(['2021-07-06 09:00:00', '2021-07-07 09:00:00'], freq='D')
        )
        assert_frame_equal(expected, daily_from_hourly(source, ['foo_max', 'foo_min']))

    def test_sum(self):
        source = DataFrame(
            {'foo': [1, 2, 5]},
            index=I(['2021-07-05 10:00:00', '2021-07-05 11:00:00', '2021-07-06 12:00:00'])
        )
        expected = DataFrame(
            {'foo': [3, 5]},
            index=I(['2021-07-06 09:00:00', '2021-07-07 09:00:00'], freq='D')
        )
        assert_frame_equal(expected, daily_from_hourly(source, ['foo']))

    def test_hourly_boundaries(self):
        source = DataFrame(
            {'foo':     [1, 2, 3],
             'foo_max': [1, 2, 3],
             'foo_min': [1, 2, 3]},
            index=I(['2021-07-06 08:00', '2021-07-06 09:00:00', '2021-07-06 10:00:00'])
        )
        expected = DataFrame(
            {'foo':     [3, 3],
             'foo_max': [2, 3],
             'foo_min': [1, 3]},
            index=I(['2021-07-06 09:00:00', '2021-07-07 09:00:00'], freq='D')
        )
        assert_frame_equal(expected, daily_from_hourly(source, ['foo', 'foo_max', 'foo_min']))

    def test_boundaries(self):
        source = DataFrame(
            {'foo':     [1, 2, 3],
             'foo_max': [1, 2, 3],
             'foo_min': [1, 2, 3]},
            index=I(['2021-07-06 08:59:59', '2021-07-06 09:00:00', '2021-07-06 09:00:01'])
        )
        expected = DataFrame(
            {'foo':     [3, 3],
             'foo_max': [2, 3],
             'foo_min': [1, 3]},
            index=I(['2021-07-06 09:00:00', '2021-07-07 09:00:00'], freq='D')
        )
        assert_frame_equal(expected, daily_from_hourly(source, ['foo', 'foo_max', 'foo_min']))
