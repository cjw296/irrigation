from pathlib import Path

from configurator import Config

config = Config.from_path(Path(__file__).parent / 'config.yaml')
