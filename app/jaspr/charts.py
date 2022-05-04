#!/usr/bin/env python
# file charts.py

"""Charting functionality for Jaspr"""

from math import log2
from pickle import TRUE
import numpy as np
import pandas as pd
from uuid import uuid4

from bokeh.embed import components
from bokeh.io import export_png
from bokeh.layouts import widgetbox
from bokeh.models import ColumnDataSource, Whisker
from bokeh.models.glyphs import Line
from bokeh.models.layouts import Column
from bokeh.models import TickFormatter, Label, AdaptiveTicker, FixedTicker, \
        LogTickFormatter
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn, Div
from bokeh.plotting import figure
from bokeh.util.compiler import TypeScript

from jaspr.model import JasprModel
from jaspr import app
from outlet import FunctionRegistry
import pprint


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

        if 'y_error' in source.data:
            y_axis_value = source.data['y_values']
            y_error_value = source.data['y_error']
            y_sum = np.add(y_axis_value, y_error_value)
            y_max = np.amax(y_sum) + 5
            pprint.pprint('y_max:')
            pprint.pprint(y_max)

            p = figure(
                x_axis_label=self.m.x_axis_label,
                y_axis_label=self.m.y_axis_label,
                x_axis_type=self.m.x_axis_type,
                y_range=(-5, y_max),
                title=f'{self.m.curr_experiment}: {self.m.curr_sample}')
            print(p.title)

        else:    
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

# ## Add error bars \/ \/ \/

        # y_round = np.around(y_series)        
        # y=int(y_round)     
        if 'y_error' in source.data:
            y_axis_value = source.data['y_values']
            y_error_value = source.data['y_error']
            x_axis_value = source.data['x_values']
            y_sum = np.add(y_axis_value, y_error_value)
            y_sub = np.subtract(y_axis_value, y_error_value)
            
            pprint.pprint("y_axis_value...")
            pprint.pprint(y_axis_value) 
            pprint.pprint("y_error_value...")
            pprint.pprint(y_error_value) 
            pprint.pprint("y_sum...")
            pprint.pprint(y_sum) 
            pprint.pprint("y_sub...")
            pprint.pprint(y_sub) 
            pprint.pprint("x_axis_value...")
            pprint.pprint(x_axis_value) 

            source_error = ColumnDataSource(dict(base=x_axis_value, upper=y_sum, lower=y_sub))

            whisker = Whisker(dimension="height", source=source_error, base='base', \
                upper='upper', lower='lower', line_color='#1c2b46', line_width=2)
            whisker.upper_head.line_color='#1c2b46'
            whisker.lower_head.line_color='#1c2b46'
            whisker.upper_head.line_width=2
            whisker.lower_head.line_width=2
            p.add_layout(whisker)  

            p.circle(x='x_values', y=y_series, size=10,
                source=source)
                            
# # ## Add error bars /\ /\ /\

        else:
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

            ## Find dilution @ ICP ~1000
            pd.set_option("display.precision", 10)

            y_rounded = np.around(y, decimals=0)
            print(y_rounded)
            pprint.pprint(y_rounded)
            pd.to_numeric(x)
            pd.to_numeric(y_rounded)    
            yx = pd.DataFrame({'y':y_rounded, 'x':x})
            #print(yx)
            yx.astype(int)
                   
            lsource = ColumnDataSource({'x': x, 'y': y})

            glyph = Line(x='x', y='y', line_color='#3aaf13',
                    line_width=3, line_alpha=0.6)

            p.add_glyph(lsource, glyph)

            chart_labels = [fit_function.description]
            for key, value in labels.items():
                value = int(float(value) * 1000000) if key == 'IC50' else value
                chart_labels.append(f' - {key}: {value}')

            #add label
            offset = 3
            for text in chart_labels[::-1]:
                label = Label(x=10, y=offset*16, y_offset=375,
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
        source = self.m.curr_datasource_fraction

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


# # Add FRNT Charting Functionality \/ \/ \/ -------------------
# class FRNTChart(object):
#     """Chart artifacts based on a common data model"""

#     def __init__(self):
#         self.m = JasprModel()
#         pprint.pprint("self.m - -FRNT- - ")
#         pprint.pprint(self.m)
#         self.fit_margin = 0.15
#         self.fit_resolution = 65

#     def _create_FRNTchart(self):
#         """Create HTML and Javascript components that will display a chart
#             for the current experiment and sample of a model

#             Returns:
#                 HTML string and JavaScript string

#         """

#         def get_x_spacing():
#             x = source.data['x_values']

#             if self.m.x_axis_type == 'log':
#                 min_x = log2(min(x))
#                 max_x = log2(max(x))
#                 extra = (max_x - min_x) * self.fit_margin
#                 return np.logspace(min_x-extra, max_x+extra,
#                     len(x)*self.fit_resolution, False, 2)
#             else:
#                 extra = (max(x) - min(x)) * self.fit_margin
#                 return np.linspace(min(x)-extra,
#                         max(x)+extra, len(x)*self.fit_resolution, False)

#         # Create the figure: p and chart the data
#         source = self.m.curr_datasource
#         FRNTp = figure(
#                 x_axis_label=self.m.x_axis_label,
#                 y_axis_label=self.m.y_axis_label,
#                 x_axis_type=self.m.x_axis_type,
#                 title=f'{self.m.curr_experiment}: {self.m.curr_sample}')
#         print(FRNTp.title)

#         # change from base 10 to base 2
#         if self.m.x_axis_type == 'log':
#             FRNTp.xaxis.ticker = FixedTicker(ticks=sorted([1/40, 1/160, 1/640, 1/2560, 1/10240,
#                 1/40960, 1/163840, 1/655360]))
#             #p.xaxis.ticker = AdaptiveTicker(mantissas=[1/5], base=2,
#             #        min_interval=1/32, max_interval=1/4, desired_num_ticks=8)
#             FRNTp.xaxis.formatter = AntigenicFormatter()
#             #p.xaxis.formatter = LogTickFormatter()
#             #p.xaxis.minor_tick_line_color = None
#             FRNTp.x_range.flipped = True
#             FRNTp.xaxis.major_label_orientation = .70

#         y_series = 'y_corrected' if self.m.blank_correction else 'y_values'
#         FRNTp.circle(x='x_values', y=y_series, size=10,
#                 source=source)

#         # could loop over plugins collection to get names and descriptions
#         if self.m.show_fit:
#             plugin_name = self.m.curr_function
#             fit_function = FunctionRegistry.plugins[plugin_name]()
#             fit_result = fit_function(self.m.x_array, self.m.y_array)
#             x = get_x_spacing()
#             y = fit_function._calculate(fit_result.x, x)
#             labels = fit_function.labels(fit_result.x)

#             ## Find dilution @ ICP ~1000
#             pd.set_option("display.precision", 10)

#             #print("x=")
#             #pprint.pprint(x)
#             #print("y=")
#             #pprint.pprint(y)
#             y_rounded = np.around(y, decimals=0)
#             #print(y_rounded)
#             #pprint.pprint(y_rounded)
#             pd.to_numeric(x)
#             pd.to_numeric(y_rounded)    
#             yx = pd.DataFrame({'y':y_rounded, 'x':x})
#             #print(yx)
#             yx.astype(int)
#             #print(yx)

#             # # Add dilutions at ICP ~1000 to chart
#             #print("ICP_1000")
#             #ICP_1000 = yx.query("950 <= y <= 1050")
#             #print(ICP_1000)

#             #ICP1000 = fit_function(y[259])
#             #print('ICP1000=')
#             #pprint.pprint(ICP1000)            
            
#             lsource = ColumnDataSource({'x': x, 'y': y})
#             glyph = Line(x='x', y='y', line_color='#3aaf13',
#                     line_width=3, line_alpha=0.6)
#             FRNTp.add_glyph(lsource, glyph)

#             chart_labels = [fit_function.description]
#             for key, value in labels.items():
#                 value = int(float(value) * 1000000) if key == 'IC50' else value
#                 chart_labels.append(f' - {key}: {value}')

#             #add label
#             offset = 3
#             for text in chart_labels[::-1]:
#                 label = Label(x=10, y=offset*16, y_offset=375,
#                         x_units='screen', y_units='screen',
#                         text=text, render_mode='css',
#                         background_fill_color='white',
#                         background_fill_alpha=0.7)
#                 FRNTp.add_layout(label)
#                 offset += 1
#             return FRNTp

#     def _get_FRNTchart_component(self):
#         return components(self._create_FRNTchart())

#     def _get_table_component(self):
#         """Create HTML and Javascript components that will display a table
#            for the current experiment and sample of a model

#             Returns:
#                 HTML string and JavaScript string

#         """
#         source = self.m.curr_datasource_fraction

#         bcols = [TableColumn(field=c, title=c) for c in source.column_names]

#         #Todo: pull out to its own function and make more robust
#         #change the column format to date for any field called "date"
#         for col in bcols:
#             if col.field =="date":
#                 col.formatter = DateFormatter()

#         data_table = DataTable(source=source, columns=bcols, height=580)
#         title = Div(text=f'<strong>{self.m.curr_experiment}: {self.m.curr_sample}</strong>')
#         return components(widgetbox(title, data_table))

#     def get_FRNTpngs(self):
#         FRNTpng_list = []
#         #for experiment in self.m.experiment_list:
#         #    self.m.curr_experiment = experiment
#         for sample in self.m.sample_list:
#             self.m.curr_sample = sample
#             FRNTp = self._create_FRNTchart()
#             FRNTp.toolbar_location=None
#             pngFile_temp = f"{uuid4()}.png"
#             export_png(FRNTp, filename=f"tmp/{pngFile_temp}")
#             png_list.append(pngFile_temp)
#         return FRNTpng_list

#     def __call__(self):
#         values = {}
#         values['FRNT_script'], values['FRNT_div'] = self._get_FRNTchart_component()
#         # values['g_script'], values['g_div'] = self._get_chart_component()
#         values['t_script'], values['t_div'] = self._get_table_component()

#         return values        
# # FRNT Charting Functionality /\ /\ /\