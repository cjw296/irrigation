#!/usr/bin/env python
from argparse import ArgumentParser
from csv import DictReader
from datetime import datetime, timedelta
from io import StringIO
from typing import Iterable, List

import pandas as pd
import requests
from sqlalchemy.orm import Session

from db import connect
from schema import Observation

RANGE_LIMITS = {
    'climat0900': 25,
    '1hour_Level2': 4,
}


def download(dataset: str, variables: List[str], start: datetime, end: datetime) -> Iterable[dict]:
    response = requests.get(
        f'https://metdata.reading.ac.uk/ext/dataset/{dataset}/get_data',
        params=dict(
            token='public',
            start_date=start.strftime('%Y-%m-%d-%H:%M:%S'),
            end_date=end.strftime('%Y-%m-%d-%H:%M:%S'),
            var=variables,
            data_format='csv'
        ))
    response.raise_for_status()
    reader = DictReader(StringIO(response.text))
    try:
        next(reader)  # units
    except StopIteration:
        # empty?
        return
    yield from reader


def time_periods(dataset: str, start: datetime, end: datetime):
    points = pd.date_range(start, end, freq=f'{RANGE_LIMITS[dataset]}D', closed='left')
    section_end = start
    for section_start, section_end in zip(points, points[1:]):
        yield section_start, section_end
    yield section_end, end


def retrieve(dataset: str, variables: List[str], start: datetime, end: datetime = None):
    end = end or datetime.now()
    for start, end in time_periods(dataset, start, end):
        yield from download(dataset, variables, start, end)


def main():
    now = datetime.now()

    parser = ArgumentParser()
    parser.add_argument('dataset')
    parser.add_argument('variables', nargs='+')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--start', type=pd.Timestamp, default=now-timedelta(days=7))
    group.add_argument('--days', type=int)
    parser.add_argument('--end', type=pd.Timestamp, default=now)
    args = parser.parse_args()

    start = (pd.Timestamp.now() - timedelta(days=args.days)).floor('D') if args.days else args.start

    session = Session(connect(), future=True)
    session.query(Observation).where(
        Observation.timestamp.between(start, args.end),
        Observation.dataset == args.dataset,
        Observation.variable.in_(args.variables)

    ).delete(synchronize_session=False)

    for row in retrieve(args.dataset, args.variables, start, args.end):
        print(row)
        for variable in args.variables:
            session.add(Observation(
                timestamp=row['TimeStamp'],
                dataset=args.dataset,
                variable=variable,
                value=row[variable]
            ))
    session.commit()


if __name__ == '__main__':
    main()
