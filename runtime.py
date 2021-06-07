from argparse import ArgumentParser

from sqlalchemy.orm import Session

from calc import mm_to_m3
from config import config
from data import connect
from schema import Area, Water


def main():
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--height', type=int,
                       help='height to drop in tank, defaults to current down to min')
    group.add_argument('--no-refill', action='store_false', dest='refill')
    args = parser.parse_args()

    session = Session(connect(), future=True)

    refilling_mm = 0
    if args.height:
        mm = args.height
        print(f'Using {mm}mm of tank water with no refilling:')
    else:
        tank_levels =session.query(Water.mm).filter_by(area_name='tanks')
        current = tank_levels.order_by(Water.timestamp.desc()).limit(1).scalar()
        if args.refill:
            mm = current - config.tanks.tap if current > config.tanks.tap else 0
            refilling_mm = min(current, config.tanks.tap) - config.tanks.min
            print(f'Starting from {current} mm, '
                  f'using {mm}mm without refilling, {refilling_mm}mm while refilling:')
        else:
            mm = current - config.tanks.min
            print(f'Starting from {current} mm, using {mm}mm:')

    tank_area = session.query(Area.size).filter_by(name='tanks').scalar()

    volume_without_refill = mm_to_m3(mm, tank_area)
    volume_with_refill = mm_to_m3(refilling_mm, tank_area)
    refill_rate = mm_to_m3(config.tanks.refill, tank_area)

    for area in session.query(Area).where(Area.irrigation_rate > 0):
        area_rate = mm_to_m3(area.irrigation_rate, area.size)
        runtime = 0
        runtime += volume_without_refill/area_rate
        runtime += volume_with_refill/(area_rate-refill_rate)
        print(f'Can water {area.name} for {runtime:.0f} mins.')


if __name__ == '__main__':
    main()
