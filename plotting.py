from collections import Sequence
from itertools import cycle

from bokeh.models import LinearAxis, Range1d, Legend, BoxAnnotation
from bokeh.palettes import Category10_10
from bokeh.plotting import figure, show
from pandas import DataFrame, Timestamp, Series

LEVELS = [
    'Water',
    'Saturation Capacity',
    'Field Capacity',
    'Refill Point',
    'Permanent Wilting Point'
]

CHANGES = [
    'Rain',
    'Irrigation',
    'Evapotranspiration'
]


def plot_water_model(data: DataFrame, annotations: Sequence[BoxAnnotation] = (),
                     title: str = None,
                     left_series: Sequence[Series] = (),
                     right_series: Sequence[Series] = ()):
    p = figure(sizing_mode='scale_width', height=150, title=title,
               x_axis_type="datetime", x_range=(Timestamp('2021'), data.index.max()),
               tools='xpan,pan,xwheel_zoom,wheel_zoom,reset',
               active_drag='xpan', active_scroll='xwheel_zoom')
    for annotation in annotations:
        p.add_layout(annotation)
    p.xaxis.formatter.months = '%b %y'
    p.xaxis.formatter.days = '%d %b'
    p.add_layout(LinearAxis(y_range_name="y2"), 'right')
    p.extra_y_ranges['y2'] = Range1d(0, 20)
    p.add_layout(
        Legend(label_text_font_size='7px', label_height=10, spacing=0, glyph_height=10), 'right'
    )

    colors = cycle(Category10_10)

    for series, color in zip(LEVELS, colors):
        p.line(data.index, data[series], color=color, legend_label=series)

    for series, color in zip(CHANGES, colors):
        p.step(data.index, data[series], color=color, legend_label=series, y_range_name='y2')

    for series, color in zip(left_series, colors):
        p.line(series.index, series, color=color, legend_label=series.name)

    for series, color in zip(right_series, colors):
        p.step(series.index, series, color=color, legend_label=series.name, y_range_name='y2')

    show(p)
