#!/usr/bin/env python
# file model.py

"""The data and state of the application

Change log:
    2019-02-01 JAS: Refactored

"""

# python imports
import json
import numpy as np
from bokeh.models import ColumnDataSource

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
        return list(ParserRegistry.plugins)

    @property
    def experiment_list(self):
        """List experiments in the current context"""
        return list(self.experiments)

    @property
    def sample_list(self):
        return list(self.experiments[self.curr_experiment]['data'])

    @property
    def curr_datasource(self):
        return ColumnDataSource(
            self.experiments[self.curr_experiment]['data'][self.curr_sample])

    @property
    def x_array(self):
        x_series = 'x_fit' if self.x_axis_type == 'log' else 'x_values'
        return np.asarray(
                self.experiments[self.curr_experiment]['data'][self.curr_sample][x_series])

    @property
    def y_array(self):
        y_series = 'y_corrected' if self.blank_correction else 'y_values'
        return np.asarray(
                self.experiments[self.curr_experiment]['data'][
                        self.curr_sample][y_series])

    @property
    def x_axis_label(self):
        experiment = self.experiments[self.curr_experiment]
        return experiment['x_axis_label']

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
