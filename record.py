from argparse import ArgumentParser
from datetime import datetime

from dateutil.parser import parse as parse_date
from sqlalchemy.orm import Session

from data import connect
from schema import Area, Observation, Water


def irrigation(session: Session, area: str, minutes: float, at: datetime):
    mm_min = session.query(Area.irrigation_rate).filter_by(name=area).scalar()
    if mm_min is None:
        raise KeyError(f'{area!r} not found')
    session.add(Observation(
        timestamp=at,
        dataset='local',
        variable='irrigation',
        area_name=area,
        value=round(mm_min*minutes, 1),
    ))


def level(session: Session, area: str, mm: float, at: datetime):
    session.add(Water(
        timestamp=at,
        area_name=area,
        source='local',
        mm=mm,
    ))


recorders = {f.__name__: f for f in (irrigation, level)}


def main():
    parser = ArgumentParser()
    parser.add_argument('type', choices=list(recorders))
    parser.add_argument('measurement', nargs='+', help='area:value')
    parser.add_argument('--at', default=datetime.now(), type=parse_date)
    args = parser.parse_args()

    recorder = recorders[args.type]
    session = Session(connect(), future=True)

    for measurement in args.measurement:
        area, value = measurement.split(':')
        value = float(value)
        recorder(session, area, value, args.at)

    session.commit()


if __name__ == '__main__':
    main()
