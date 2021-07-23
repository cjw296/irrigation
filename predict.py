from argparse import ArgumentParser
from datetime import datetime, date, timedelta, time

from dateutil.parser import parse as parse_date
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from calc import mm_to_m3
from config import config
from data import connect
from download import main as download
from schema import Observation, Area

WEEKLY_DESIRED_MM = 25.4


def last_sunday():
    dt = date.today()
    while dt.strftime('%a') != 'Sun':
        dt -= timedelta(days=1)
    return datetime.combine(dt, time(0, 0))


def reading_uni_rainfall(session, start, end):
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


def print_mm_still_needed(area, mm_per_min, rain, required=WEEKLY_DESIRED_MM):
    received = rain
    pct = received/required
    still_needed = max(required-received, 0)/mm_per_min
    print(f'{area.capitalize()} has had {received:.1f} mm ({pct:.0%}) '
          f'and needs {still_needed:.0f} mins of watering.', end=' ')


def comma_ints(text):
    return sum(int(t) for t in text.split(','))


def main():
    now = datetime.now()
    parser = ArgumentParser()
    parser.add_argument('--start', default=now-timedelta(days=7), type=parse_date)
    parser.add_argument('--end', default=now, type=parse_date)
    args = parser.parse_args()

    download(['config'])
    session = Session(connect(), future=True)

    print()
    rain = reading_uni_rainfall(session, args.start, args.end)

    tank_current = config.tanks.tap
    tank_pct = tank_current / config.tanks.max
    print(f'Tanks currently at {tank_current:.0f}mm ({tank_pct:.0%})')
    tank_size = session.query(Area.size).filter_by(name='tanks').scalar()

    tank_volume = mm_to_m3(tank_current, tank_size)
    tank_tap = mm_to_m3(config.tanks.tap, tank_size)
    tank_min = mm_to_m3(config.tanks.min, tank_size)
    refill_rate = mm_to_m3(config.tanks.refill, tank_size)

    print()
    for area in session.query(Area).where(Area.irrigation_rate > 0):
        print_mm_still_needed(area.name, area.irrigation_rate, rain)
        area_rate = mm_to_m3(area.irrigation_rate, area.size)

        runtime = 0
        if tank_volume > tank_tap:
            runtime += (tank_volume - tank_tap)/area_rate
        runtime += (max(tank_volume, tank_tap)-tank_min)/(area_rate-refill_rate)
        print(f'Tank can support {runtime:.0f} mins watering.')


if __name__ == '__main__':
    main()
