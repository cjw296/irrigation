#!/usr/bin/env python
from argparse import ArgumentParser
from csv import DictReader
from datetime import datetime, timedelta
from io import StringIO
from typing import Iterable, List

import pandas as pd
import requests
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from config import config
from data import connect
from schema import Observation

RANGE_LIMITS = {
    'climat0900': 25,
    '1hour_Level2': 4,
    '1hour_Level2_maxmin': 4,
    'climate_extract.cgi': 10,
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
        yield section_start, section_end-pd.Timedelta(seconds=1)
    yield section_end, end


def retrieve(dataset: str, variables: List[str], start: datetime, end: datetime = None):
    end = end or datetime.now()
    for start, end in time_periods(dataset, start, end):
        yield from download(dataset, variables, start, end)


def sync(session, dataset: str, variables: List[str],
         start: pd.Timestamp, end: pd.Timestamp, debug: bool):

    session.query(Observation).where(
        Observation.timestamp.between(start, end),
        Observation.dataset == dataset,
        Observation.variable.in_(variables)

    ).delete(synchronize_session=False)

    obs_count = row_count = 0
    latest_timestamp = start
    for row_count, row in enumerate(retrieve(dataset, variables, start, end), start=1):
        if debug:
            print(f'{dataset}:', ' '.join(f'{k}={v}' for k, v in row.items()))
        for variable in variables:
            value = row[variable]
            if value == '':
                continue
            timestamp = pd.Timestamp(row['TimeStamp'])
            latest_timestamp = max(latest_timestamp, timestamp)
            session.add(Observation(
                timestamp=timestamp,
                dataset=dataset,
                variable=variable,
                value=value
            ))
            obs_count += 1
    print(f'{dataset}: {row_count} rows giving {obs_count} observations, '
          f'latest at {latest_timestamp}')
    session.commit()


def main(args=None):
    now = datetime.now()

    parser = ArgumentParser()
    parser.add_argument('dataset')
    parser.add_argument('variables', nargs='*')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--start', type=pd.Timestamp, default=now-timedelta(days=7))
    group.add_argument('--days', type=int)
    parser.add_argument('--end', type=pd.Timestamp, default=now)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args(args)

    start = (pd.Timestamp.now() - timedelta(days=args.days)).floor('D') if args.days else args.start

    session = Session(connect(), future=True)

    parameter_sets = []
    if args.dataset == 'config':
        for dataset, variables in config.observations.items():
            rows = session.execute(
                select(Observation.variable, func.max(Observation.timestamp)).
                where(Observation.variable.in_(variables)).
                group_by(Observation.variable)
            )
            try:
                dataset_start = min(row[1] for row in rows)+timedelta(seconds=1)
            except ValueError:
                parser.error(f'Need to explicitly download {dataset} as least once!')
            else:
                parameter_sets.append((dataset, variables.data, dataset_start, args.end))
    else:
        if not args.variables:
            parser.error('variables must be specified')
        parameter_sets.append((args.dataset, args.variables, start, args.end))

    for parameter_set in parameter_sets:
        sync(session, *parameter_set, debug=args.debug)


if __name__ == '__main__':
    main()
