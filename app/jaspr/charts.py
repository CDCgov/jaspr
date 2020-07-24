#!/usr/bin/env python
# file charts.py

"""Charting functionality for Jaspr"""

from math import log2
import numpy as np
from uuid import uuid4


from bokeh.embed import components
from bokeh.io import export_png
from bokeh.layouts import widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.glyphs import Line
from bokeh.models import TickFormatter, Label, AdaptiveTicker, FixedTicker, \
        LogTickFormatter
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn, Div
from bokeh.plotting import figure
from bokeh.util.compiler import TypeScript

from jaspr.model import JasprModel
from jaspr import app
from outlet import FunctionRegistry


TS_CODE = """
import {TickFormatter} from "models/formatters/tick_formatter"

export class AntigenicFormatter extends TickFormatter {
    doFormat(ticks: string[] | number[]) {
        let formatted = []
        for (let tick of ticks) {
            let val = 1000000 * Number(tick)
            let titer = String(val.toFixed())
            formatted.push(titer)
        }
    return formatted
    }
}
"""


class AntigenicFormatter(TickFormatter):

    __implementation__ = TypeScript(TS_CODE)


class JasprChart(object):
    """Chart artifacts based on a common data model"""

    def __init__(self):
        self.m = JasprModel()
        self.fit_margin = 0.15
        self.fit_resolution = 65

    def _create_chart(self):
        """Create HTML and Javascript components that will display a chart
            for the current experiment and sample of a model

            Returns:
                HTML string and JavaScript string

        """

        def get_x_spacing():
            x = source.data['x_values']
            if self.m.x_axis_type == 'log':
                min_x = log2(min(x))
                max_x = log2(max(x))
                extra = (max_x - min_x) * self.fit_margin
                return np.logspace(min_x-extra, max_x+extra,
                    len(x)*self.fit_resolution, False, 2)
            else:
                extra = (max(x) - min(x)) * self.fit_margin
                return np.linspace(min(x)-extra,
                        max(x)+extra, len(x)*self.fit_resolution, False)

        # Create the figure: p and chart the data
        source = self.m.curr_datasource
        p = figure(
                x_axis_label=self.m.x_axis_label,
                y_axis_label=self.m.y_axis_label,
                x_axis_type=self.m.x_axis_type,
                title=f'{self.m.curr_experiment}: {self.m.curr_sample}')
        print(p.title)

        # change from base 10 to base 2
        if self.m.x_axis_type == 'log':
            p.xaxis.ticker = FixedTicker(ticks=sorted([1/40, 1/160, 1/640, 1/2560, 1/10240,
                1/40960, 1/163840, 1/655360]))
            #p.xaxis.ticker = AdaptiveTicker(mantissas=[1/5], base=2,
            #        min_interval=1/32, max_interval=1/4, desired_num_ticks=8)
            p.xaxis.formatter = AntigenicFormatter()
            #p.xaxis.formatter = LogTickFormatter()
            #p.xaxis.minor_tick_line_color = None
            p.x_range.flipped = True
            p.xaxis.major_label_orientation = .70

        y_series = 'y_corrected' if self.m.blank_correction else 'y_values'
        p.circle(x='x_values', y=y_series, size=10,
                source=source)

        # could loop over plugins collection to get names and descriptions
        if self.m.show_fit:
            plugin_name = self.m.curr_function
            fit_function = FunctionRegistry.plugins[plugin_name]()
            fit_result = fit_function(self.m.x_array, self.m.y_array)
            x = get_x_spacing()
            y = fit_function._calculate(fit_result.x, x)
            labels = fit_function.labels(fit_result.x)

            lsource = ColumnDataSource({'x': x, 'y': y})
            glyph = Line(x='x', y='y', line_color='#3aaf13',
                    line_width=3, line_alpha=0.6)
            p.add_glyph(lsource, glyph)

            chart_labels = [fit_function.description]
            for key, value in labels.items():
                value = int(float(value) * 1000000) if key == 'IC50' else value
                chart_labels.append(f' - {key}: {value}')

            #add label
            offset = 1
            for text in chart_labels[::-1]:
                label = Label(x=10, y=offset*20, y_offset=375,
                        x_units='screen', y_units='screen',
                        text=text, render_mode='css',
                        background_fill_color='white',
                        background_fill_alpha=0.7)
                p.add_layout(label)
                offset += 1
        return p

    def _get_chart_component(self):
        return components(self._create_chart())

    def _get_table_component(self):
        """Create HTML and Javascript components that will display a table
           for the current experiment and sample of a model

            Returns:
                HTML string and JavaScript string

        """
        source = self.m.curr_datasource

        bcols = [TableColumn(field=c, title=c) for c in source.column_names]

        #Todo: pull out to its own function and make more robust
        #change the column format to date for any field called "date"
        for col in bcols:
            if col.field =="date":
                col.formatter = DateFormatter()

        data_table = DataTable(source=source, columns=bcols, height=580)
        title = Div(text=f'<strong>{self.m.curr_experiment}: {self.m.curr_sample}</strong>')

        return components(widgetbox(title, data_table))

    def get_pngs(self):
        png_list = []
        #for experiment in self.m.experiment_list:
        #    self.m.curr_experiment = experiment
        for sample in self.m.sample_list:
            self.m.curr_sample = sample
            p = self._create_chart()
            p.toolbar_location=None
            pngFile_temp = f"{uuid4()}.png"
            export_png(p, filename=f"tmp/{pngFile_temp}")
            png_list.append(pngFile_temp)

        return png_list

    def __call__(self):
        values = {}
        values['g_script'], values['g_div'] = self._get_chart_component()
        values['t_script'], values['t_div'] = self._get_table_component()
        return values
