from argparse import ArgumentParser
from csv import reader as csv_reader
from datetime import datetime, date, timedelta, time
from io import StringIO

from dateutil.parser import parse as parse_date
import requests

# https://metdata.reading.ac.uk/ext/dataset/climat0900/get_data?token=public&start_date=2020-08-01-18:50:27&end_date=2020-08-13-18:50:27&var=Rain_accum_0909&missing=NaN&data_format=csv
# https://metdata.reading.ac.uk/ext/dataset/1hour_Level2/get_data?token=public&start_date=2020-08-06-00:00:00&end_date=2020-08-13-22:49:27&var=Rain&var=Rain_accum_der&missing=NaN&data_format=csv'


def last_sunday():
    dt = date.today()
    while dt.strftime('%a') != 'Sun':
        dt -= timedelta(days=1)
    return datetime.combine(dt, time(0, 0))


def reader(content):
    r = csv_reader(StringIO(content))
    next(r)  # header
    next(r)  # units
    for dt, value in r:
        yield parse_date(dt), float(value)


def download(series, var, start, end):
    response = requests.get(
        f'https://metdata.reading.ac.uk/ext/dataset/{series}/get_data',
        params=dict(
            token='public',
            start_date=start.strftime('%Y-%m-%d-%H:%M:%S'),
            end_date=end.strftime('%Y-%m-%d-%H:%M:%S'),
            var=var,
            data_format='csv'
        ))
    response.raise_for_status()
    return reader(response.content.decode())


def reading_uni_rainfall(start, end):
    rain = 0.0
    earliest = None
    for start, value in download('climat0900', 'Rain_accum_0909', start+timedelta(days=1), end):
        if earliest is None:
            earliest = start-timedelta(days=1)
        rain += value
    start += timedelta(hours=1)
    for start, value in download('1hour_Level2', 'Rain', start, end):
        rain += value

    latest = start

    print(f'Between {earliest} and {latest}, {rain:.1f}mm of rain has fallen')
    return rain


def main():
    parser = ArgumentParser()
    parser.add_argument('--start', default=last_sunday(), type=parse_date)
    parser.add_argument('--end', default=datetime.now(), type=parse_date)
    args = parser.parse_args()
    rain = reading_uni_rainfall(args.start, args.end)


if __name__ == '__main__':
    main()
