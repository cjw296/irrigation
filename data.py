from pandas import read_sql
from sqlalchemy import create_engine

from config import config


def db_url():
    db = config.storage
    return f"postgresql://{db.username}:{db.password}@{db.host}/{db.database}"


def connect():
    return create_engine(db_url(), echo=False)


def load_daily():
    return read_sql("select * from observation where dataset='climat0900'", db_url()).pivot(
        index='timestamp', columns='variable', values='value'
    )


def load_hourly():
    return read_sql("select * from observation where dataset='1hour_Level2_maxmin'", db_url()).pivot(
        index='timestamp', columns='variable', values='value'
    )


def daily_from_hourly(hourly, variables):
    origin = hourly.index.min().replace(hour=9)
    resampler = hourly[variables].resample('D', origin=origin, label='right')
    return resampler.agg({v: "max" if v.endswith('max') else 'min' for v in variables})
