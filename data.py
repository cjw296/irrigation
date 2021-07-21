from datetime import datetime
from typing import Sequence

from pandas import read_sql, DataFrame
from sqlalchemy import create_engine, select

from config import config
from schema import Observation


def db_url():
    db = config.storage
    return f"postgresql://{db.username}:{db.password}@{db.host}/{db.database}"


def connect():
    return create_engine(db_url(), echo=False)


def load(dataset: str, start: datetime = None) -> DataFrame:
    query = select(Observation).where(Observation.dataset == dataset)
    if start:
        query = query.where(Observation.timestamp >= start)
    return read_sql(query, db_url()).pivot(
        index='timestamp', columns='variable', values='value'
    )


def load_daily(start: datetime = None) -> DataFrame:
    return load('climat0900', start)


def load_hourly(start: datetime = None) -> DataFrame:
    return load('1hour_Level2', start)


def load_hourly_maxmin(start: datetime = None) -> DataFrame:
    return load('1hour_Level2_maxmin', start)


def agg_from_variable(variable: str) -> str:
    if variable.endswith('max'):
        return 'max'
    elif variable.endswith('min'):
        return 'min'
    else:
        return 'sum'


def daily_from_hourly(hourly: DataFrame, variables: Sequence[str]) -> DataFrame:
    origin = hourly.index.min().replace(hour=9)
    resampler = hourly[variables].resample('D', origin=origin, label='right', closed='right')
    return resampler.agg({v: agg_from_variable(v) for v in variables})


def combined_data(start: datetime = None) -> DataFrame:
    daily = load_daily(start)
    hourly = load_hourly_maxmin(start)
    daily[['P_max', 'P_min']] = daily_from_hourly(hourly, ['P_max', 'P_min']) * 0.1  # hPa to kPa
    daily[['RH_max', 'RH_min']] = daily_from_hourly(hourly, ['RH_max', 'RH_min'])
    return daily
