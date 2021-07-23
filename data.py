from datetime import datetime
from typing import Sequence, Union

from pandas import (
    read_sql, DataFrame, Series, Timedelta, concat, Timestamp, to_datetime,
    date_range
)

from sqlalchemy import create_engine, select, or_, func
from sqlalchemy.orm import Session

from config import config
from schema import Observation


def db_url():
    db = config.storage
    return f"postgresql://{db.username}:{db.password}@{db.host}/{db.database}"


def connect():
    return create_engine(db_url(), echo=False)


def just_after(source: Union[str, DataFrame, Series, datetime, Timestamp]) -> Timestamp:
    if isinstance(source, (DataFrame, Series)):
        source = source.index.max()
    return to_datetime(source) + Timedelta(seconds=1)


def datetime_range(start: datetime, end: datetime, offset:Timedelta = Timedelta("9h")):
    idx = date_range(start, end, normalize=True) + offset
    return idx[(idx >= start) & (idx <= end)]


def load(dataset: str, start: datetime = None, variables: Sequence[str] = None) -> DataFrame:
    query = select(Observation).where(Observation.dataset == dataset)
    if start:
        query = query.where(Observation.timestamp >= start)
    if variables:
        query = query.where(or_(Observation.variable == v for v in variables))
    return read_sql(query, db_url()).pivot(
        index='timestamp', columns='variable', values='value'
    )


def load_daily(start: datetime = None, variables: Sequence[str] = None) -> DataFrame:
    return load('climat0900', start, variables)


def load_hourly(start: datetime = None, variables: Sequence[str] = None) -> DataFrame:
    return load('1hour_Level2', start, variables)


def load_hourly_maxmin(start: datetime = None, variables: Sequence[str] = None) -> DataFrame:
    return load('1hour_Level2_maxmin', start, variables)


def agg_from_variable(variable: str) -> str:
    if variable.endswith('max'):
        return 'max'
    elif variable.endswith('min'):
        return 'min'
    else:
        return 'sum'


def daily_from_hourly(hourly: DataFrame, variables: Sequence[str]) -> DataFrame:
    base = hourly.index.min()
    origin = base.normalize()
    if base - origin > Timedelta(hours=9):
        origin += Timedelta(days=1)
    origin += Timedelta(hours=9)
    resampler = hourly[variables].resample('D', origin=origin, label='right', closed='right')
    return resampler.agg({v: agg_from_variable(v) for v in variables})


def daily_rainfall(start: datetime = None) -> Series:
    manual = load('climate_extract_cgi', start)['RR']
    auto = load('climat0900', start=just_after(manual), variables=['Rain_accum_0909'])
    if auto.empty:
        return manual
    return concat([manual, auto['Rain_accum_0909']])


def recent_rainfall() -> Series:
    session = Session(connect(), future=True)
    start = session.query(func.max(Observation.timestamp)).where(
        Observation.variable.in_(['Rain_accum_0909', 'RR'])
    ).scalar()
    data = load_hourly(start=just_after(start), variables=['Rain'])
    if data.empty:
        return Series(dtype='float64')
    return daily_from_hourly(data, ['Rain'])['Rain']


def combined_data(start: datetime = None) -> DataFrame:
    daily = load_daily(start)
    hourly = load_hourly_maxmin(start)
    daily[['P_max', 'P_min']] = daily_from_hourly(hourly, ['P_max', 'P_min']) * 0.1  # hPa to kPa
    daily[['RH_max', 'RH_min']] = daily_from_hourly(hourly, ['RH_max', 'RH_min'])
    daily['Rain'] = daily_rainfall(start)
    return daily
