from argparse import ArgumentParser
from datetime import datetime

from dateutil.parser import parse as parse_date
from pandas import Timestamp
from sqlalchemy.orm import Session

from config import config
from data import connect
from schema import Observation, Water


def irrigation(session: Session, area: str, minutes: float, at: datetime):
    session.add(Observation(
        timestamp=at,
        dataset='local',
        variable='irrigation',
        area_name=area,
        value=int(minutes),
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
    parser.add_argument('area', )
    parser.add_argument('value')
    parser.add_argument('--at', default=Timestamp.now(), type=Timestamp)
    args = parser.parse_args()

    recorder = recorders[args.type]
    session = Session(connect(), future=True)

    value = float(config.tanks.get(args.value, args.value))
    recorder(session, args.area, value, args.at)

    session.commit()


if __name__ == '__main__':
    main()
