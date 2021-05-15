from argparse import ArgumentParser
from datetime import datetime, date, timedelta, time

from dateutil.parser import parse as parse_date
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from data import connect
from schema import Observation

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


def reading_uni_rainfall(start, end):
    session = Session(connect(), future=True)
    rain, earliest, latest = session.execute(
        select(
            func.sum(Observation.value),
            func.min(Observation.timestamp),
            func.max(Observation.timestamp),
        ).where(
            Observation.dataset == '1hour_Level2',
            Observation.variable == 'Rain',
            Observation.timestamp.between(start, end),
        )
    ).one()
    print(f'Between {earliest:%a %d %b %H:%M} and {latest:%a %d %b %H:%M}, '
          f'{rain:.1f}mm of rain has fallen.')
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
    now = datetime.now()
    parser = ArgumentParser()
    parser.add_argument('--start', default=now-timedelta(days=7), type=parse_date)
    parser.add_argument('--end', default=now, type=parse_date)
    for zone in ZONE_TO_MM_PER_MIN:
        parser.add_argument('--'+zone, type=comma_ints, default=0, help='watering this week (min)')
    args = parser.parse_args()
    rain = reading_uni_rainfall(args.start, args.end)
    for zone, mm_per_min in ZONE_TO_MM_PER_MIN.items():
        print_mm_still_needed(zone, mm_per_min, rain, watering=getattr(args, zone))


if __name__ == '__main__':
    main()
