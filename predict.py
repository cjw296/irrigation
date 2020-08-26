from argparse import ArgumentParser
from csv import reader as csv_reader
from datetime import datetime, date, timedelta, time
from io import StringIO

from dateutil.parser import parse as parse_date
import requests

ZONE_TO_MM_PER_MIN = {
    'house': 0.097944482495229,
    'terrace': 0.093639004859511,
}

WEEKLY_DESIRED_MM = 25.4


def last_sunday():
    dt = date.today()
    while dt.strftime('%a') != 'Sun':
        dt -= timedelta(days=1)
    return datetime.combine(dt, time(0, 0))


def reader(content):
    r = csv_reader(StringIO(content))
    next(r)  # header
    try:
        next(r)  # units
    except StopIteration:
        # empty?
        return
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
        if earliest is None:
            earliest = start-timedelta(hours=1)
        rain += value

    latest = start

    print(f'Between {earliest} and {latest}, {rain:.1f}mm of rain has fallen.')
    return rain


def print_mm_still_needed(zone, mm_per_min, rain, watering, required=WEEKLY_DESIRED_MM):
    received = watering * ZONE_TO_MM_PER_MIN[zone] + rain
    pct = received/required
    still_needed = max(required-received, 0)/mm_per_min
    print(f'{zone.capitalize()} has had {received:.1f} mm ({pct:.0%}) '
          f'and needs {still_needed:.0f} mins of watering.')


def comma_ints(text):
    return sum(int(t) for t in text.split(','))


def main():
    parser = ArgumentParser()
    parser.add_argument('--start', default=last_sunday(), type=parse_date)
    parser.add_argument('--end', default=datetime.now(), type=parse_date)
    for zone in ZONE_TO_MM_PER_MIN:
        parser.add_argument('--'+zone, type=comma_ints, default=0, help='watering this week (min)')
    args = parser.parse_args()
    rain = reading_uni_rainfall(args.start, args.end)
    for zone, mm_per_min in ZONE_TO_MM_PER_MIN.items():
        print_mm_still_needed(zone, mm_per_min, rain, watering=getattr(args, zone))


if __name__ == '__main__':
    main()
