from sqlalchemy import Column, String, Integer, DateTime, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Area(Base):

    __tablename__ = 'area'

    name = Column(String, primary_key=True)
    irrigation_rate = Column(Float, nullable=False)  # in mm / min


class Observation(Base):

    __tablename__ = 'observation'
    __table_args__ = (
        UniqueConstraint('timestamp', 'dataset', 'variable', 'area_name'),
    )

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    dataset = Column(String, nullable=False)
    variable = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    area_name = Column(String, ForeignKey('area.name'), nullable=True)


class Water(Base):

    __tablename__ = 'water_level'

    timestamp = Column(DateTime, primary_key=True)
    area_name = Column(String, ForeignKey('area.name'), primary_key=True)
    source = Column(String)
    mm = Column(Float)
