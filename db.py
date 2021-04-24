from pathlib import Path

from configurator import Config
from sqlalchemy import create_engine


def connect():
    config = Config.from_path(Path(__file__).parent / 'config.yaml')
    db = config.storage
    return create_engine(f"postgresql://{db.username}:{db.password}@{db.host}/{db.database}")
