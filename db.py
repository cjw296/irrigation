from pathlib import Path

from configurator import Config
from sqlalchemy import create_engine


def db_url():
    config = Config.from_path(Path(__file__).parent / 'config.yaml')
    db = config.storage
    return f"postgresql://{db.username}:{db.password}@{db.host}/{db.database}"


def connect():
    return create_engine(db_url())
