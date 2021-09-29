from dataclasses import dataclass
from datetime import datetime
from typing import Union

from pandas import DataFrame, Series

from calc import evapotranspiration
from config import config
from data import combined_data

soil_config = config.soil


@dataclass
class Water:
    minimum: float = 0
    permanent_wilting_point: float = soil_config.permanent_wilting_point
    refill_point: float = soil_config.refill_point
    field_capacity: float = soil_config.field_capacity
    saturation_capacity: float = soil_config.saturation_capacity

    drain_rate: float = 3  # in days
    rain_field: str = 'Rain'
    current: float = 0

    def __post_init__(self):
        assert self.drain_rate >= 1

    def __call__(self, row):
        current = self.current
        if current > self.field_capacity:
            current -= (current - self.field_capacity) / self.drain_rate
        summed = current + row["Rain"] + row["Irrigation"] - row["Evapotranspiration"]
        self.current = min(max(summed, self.minimum), self.saturation_capacity)
        return self.current

    def run(
            self,
            data: DataFrame = None,
            irrigation: Union[float, Series] = 0,
            initial: float = None,
            start: datetime = None,
            calculate_evapotranspiration=evapotranspiration
    ) -> DataFrame:

        if data is None:
            data = combined_data(start)
        if initial is not None:
            self.current = initial
        if start is not None:
            data = data.loc[start:]

        evapotranspiration_series = calculate_evapotranspiration(data)
        data_ = DataFrame({
            'Evapotranspiration': evapotranspiration_series,
            'Rain': data[self.rain_field],
            'Irrigation': irrigation,
            'Water': self.current,
            'Field Capacity': self.field_capacity,
            'Saturation Capacity': self.saturation_capacity,
            'Refill Point': soil_config.refill_point,
            'Permanent Wilting Point': soil_config.permanent_wilting_point,
        })
        data_['Irrigation'].fillna(0, inplace=True)
        data_['Water'] = data_.fillna(0).apply(self, axis='columns')
        return data_
