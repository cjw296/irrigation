from sqlalchemy import Column, String, Integer, DateTime, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Area(Base):

    __tablename__ = 'area'

    name = Column(String, primary_key=True)
    area = Column(Integer)


class Observation(Base):

    __tablename__ = 'observation'

    timestamp = Column(DateTime, primary_key=True)
    dataset = Column(String, primary_key=True)
    variable = Column(String, primary_key=True)
    value = Column(Float)
    area_name = Column(String, ForeignKey('area.name'), nullable=True)


class Watering(Base):

    __tablename__ = 'watering'

    id = Column('id', Integer, primary_key=True)
    date = Column(Date)
    area_name = Column(String, ForeignKey('area.name'))
    source = Column(String)
    mm = Column(Float)


class Water(Base):

    __tablename__ = 'water_level'

    timestamp = Column(DateTime, primary_key=True)
    area_name = Column(String, ForeignKey('area.name'), primary_key=True)
    source = Column(String)
    mm = Column(Float)
