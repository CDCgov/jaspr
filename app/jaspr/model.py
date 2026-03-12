#!/usr/bin/env python
# file model.py

"""The data and state of the application

Change log:
    2019-02-01 JAS: Refactored

"""

# python imports
import json
import numpy as np
import pandas as pd
from bokeh.models import ColumnDataSource
from fractions import Fraction
import pprint

# flask imports
from flask import session

# app imports
from outlet import FunctionRegistry, ParserRegistry


class JasprModel(object):
    """Track state for the jaspr application."""

    def __init__(self):
        """Sync with current session or init with default data"""
        # stateful attributes must be defined, but may be set by loading
        # data from an existing session or from default values
        self.show_fit = False
        self.blank_correction = False
        self.x_axis_type = 'linear'

        # ui state settigns
        self.curr_run = ''
        self.curr_experiment = ''
        self.curr_sample = ''
        self.curr_parser = ''
        self.curr_function = 'linear'

        self.experiments = {}

        self.ensure_session()

    def set_defaults(self, settings=None):
        settings = settings or ParserRegistry.plugins['anscombe']()()
        for k, v in settings.items():
            setattr(self, k, v)
        self.update_session(default=True)

    @property
    def context(self):
        context = self.__dict__
        context['experiment_list'] = self.experiment_list
        context['function_list'] = self.function_list
        context['parser_list'] = self.parser_list
        context['sample_list'] = self.sample_list
        return context

    @property
    def function_list(self):
        """List fitting function plugins"""
        return list(FunctionRegistry.plugins)

    @property
    def parser_list(self):
        """List file parsing plugins"""
        # Hide unsupported parser options from the Load Data UI.
        return [name for name in ParserRegistry.plugins if name != 'hint_cx5']

    @property
    def experiment_list(self):
        """List experiments in the current context"""
        return list(self.experiments)

    @property
    def sample_list(self):
        return list(self.experiments[self.curr_experiment]['data'])

    @property
    def curr_datasource_fraction(self):
        sample_data = self.experiments[self.curr_experiment]['data'][self.curr_sample]
        import pprint
        pprint.pprint("sample_data:")
        pprint.pprint(sample_data)
        sample_data['x_values'] = [str(Fraction(str(a))) for a in sample_data['x_values']]
        if ('x_fit' in sample_data):
            sample_data['x_fit'] = [str(Fraction(str(a))) for a in sample_data['x_fit']]
              
        return ColumnDataSource(sample_data)

    @property
    def curr_datasource(self):

        return ColumnDataSource(self.experiments[self.curr_experiment]['data'][self.curr_sample])

    @property
    def x_array(self):
        x_series = 'x_fit' if self.x_axis_type == 'log' else 'x_values'
        
        print("x_values:")
        pprint.pprint(np.asarray(
                self.experiments[self.curr_experiment]['data'][self.curr_sample][x_series]))

        return np.asarray(
                self.experiments[self.curr_experiment]['data'][self.curr_sample][x_series])

    @property
    def y_array(self):
        y_series = 'y_corrected' if self.blank_correction else 'y_values'
        
        print("y_values:")
        pprint.pprint(np.asarray(
                self.experiments[self.curr_experiment]['data'][
                        self.curr_sample][y_series]))

        return np.asarray(
                self.experiments[self.curr_experiment]['data'][
                        self.curr_sample][y_series])
    
    @property
    def x_axis_label(self):
        experiment = self.experiments[self.curr_experiment]
        return experiment['x_axis_label']

    @property
    def y_error(self):
        experiment = self.experiments[self.curr_experiment]
        return experiment['y_error']

    @property
    def y_axis_label(self):
        experiment = self.experiments[self.curr_experiment]
        return experiment['y_axis_label']

    def update_session(self, default=False):
        """Call to manually sync session after a value change"""
        if default:
            self.curr_experiment = self.experiment_list[0]
            self.curr_sample = self.sample_list[0]
        for k, v in self.__dict__.items():
            if k in ('experiments', ):
                session[k] = json.dumps(v)
            else:
                session[k] = v
        session.modified = True

    def update_attribute(self, k, v):
        if k in ('show_fit', 'blank_correction'):
            setattr(self, k, json.loads(v))
        else:
            setattr(self, k, v)
        self.update_session()

    def ensure_session(self, reset=False):
        """Load existing session, or create a new one"""
        if reset or not all(
                [key in session for key in self.__dict__]):
            # new or invalid session state
            session.clear()

            # reset session to default state
            self.set_defaults()
        else:
            # load existing session data
            for k, v in session.items():
                if k in ('experiments', ):
                    setattr(self, k, json.loads(v))
                else:
                    setattr(self, k, v)

    
    def model_convergence():
     
        jm=JasprModel()
    
        output=BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')

        headerList = ["Virus"]
        for sample in jm.sample_list:
            headerList.append(sample)
        
        rowList = []

        for experiment in jm.experiment_list:
            rowAdd = []
            rowAdd.append(experiment)
            pprint.pprint("experiment:")
            pprint.pprint(experiment)

            for sample in jm.sample_list:
                #print("sample:")
                #pprint.pprint(sample)
                pprint.pprint("jm.experiments-")
                pprint.pprint (jm.experiments[experiment]['results'])
                rowAdd.append(jm.experiments[experiment]['results'][jm.curr_function][sample])

            rowList.append(rowAdd)

        df = pd.DataFrame(rowList, columns=headerList)
        print(df)
        df.to_excel(writer, sheet_name="Full_Report", index=False)

        writer.close()

        output.seek(0)

        convergence = make_response(send_file(output, download_name='Full_Report_' + str(datetime.now().strftime('%Y_%m_%d')) +'.xlsx', as_attachment=True))
        response.headers['cache-control'] = 'no-cache'
        return convergence

