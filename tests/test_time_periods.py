import unittest
from typing import Callable, Iterable

import pandas as pd

from data import datetime_range


class Checks:

    implementation: Callable[[pd.Timestamp, pd.Timestamp], Iterable[pd.Timestamp]]
    assertEqual: Callable[[Iterable[pd.Timestamp], Iterable[pd.Timestamp]], None]

    def check(self, result, expected):
        assert list(result) == list(pd.DatetimeIndex(expected))

    def test_start_before_end_after(self):
        result = self.implementation(
            pd.Timestamp('2021-07-05 08:10:11'),
            pd.Timestamp('2021-07-07 12:13:14')
        )
        self.check(result, ['2021-07-05 09:00:00', '2021-07-06 09:00:00', '2021-07-07 09:00:00'])

    def test_start_after_end_before(self):
        result = self.implementation(
            pd.Timestamp('2021-07-05 09:10:11'),
            pd.Timestamp('2021-07-07 08:13:14')
        )
        self.check(result, ['2021-07-06 09:00:00'])

    def test_all_datetime_bits(self):
        result = self.implementation(
            pd.Timestamp(2021, 7, 5, 8, 10, 11, 1234),
            pd.Timestamp(2021, 7, 7, 12, 13, 14, 1516),
        )
        self.check(result, ['2021-07-05 09:00:00', '2021-07-06 09:00:00', '2021-07-07 09:00:00'])

    def test_weekend(self):
        result = self.implementation(
            pd.Timestamp('2021-07-02 08:10:11'),
            pd.Timestamp('2021-07-04 09:13:14')
        )
        self.check(result, ['2021-07-02 09:00:00', '2021-07-03 09:00:00', '2021-07-04 09:00:00'])

    def test_one_second_after_nine(self):
        result = self.implementation(
            pd.Timestamp('2021-07-04 09:00:01'),
            pd.Timestamp('2021-07-07 09:35:44.964864')
        )
        self.check(result, ['2021-07-05 09:00:00', '2021-07-06 09:00:00', '2021-07-07 09:00:00'])

    def test_closed_endpoints(self):
        result = self.implementation(
            pd.Timestamp('2021-07-05 09:00:00'),
            pd.Timestamp('2021-07-07 09:00:00')
        )
        self.check(result, ['2021-07-05 09:00:00', '2021-07-06 09:00:00', '2021-07-07 09:00:00'])


class TestMethod1(Checks):
    @staticmethod
    def implementation(start, end):
        possible = pd.date_range(start.round('D') + pd.Timedelta(hours=9), end, freq='1D')
        return [ts for ts in possible if start <= ts <= end]


class TestMethod7(Checks):
    @staticmethod
    def implementation(start, end, offset=pd.Timedelta("9h")):
        idx = pd.date_range(start, end, normalize=True) + offset
        idx = idx[(idx >= start) & (idx <= end)]
        return idx


class TestActual(Checks):
    @staticmethod
    def implementation(start, end, offset=pd.Timedelta("9h")):
        return datetime_range(start, end, offset)


if __name__ == '__main__':
    unittest.main()
