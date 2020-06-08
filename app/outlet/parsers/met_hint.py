#!/usr/bin/env python

# python imports
import itertools
from collections import OrderedDict

import pandas as pd
import numpy as np

from io import StringIO
from zipfile import ZipFile

# jaspr imports
from outlet import ParserRegistry, FunctionRegistry


def fit(plugin_name, x_data, y_data):
    fitter = FunctionRegistry.plugins[plugin_name]()
    result = fitter(x_data, y_data)
    return fitter.labels(result.x)


class HintBase(object):
    """A base class for HINT parsers

    Add attributes `name` and `description` to the implementation classes

    Override _get_plate_experiments if needed

    """

    def __init__(self, keyfile, datafile):
        self.sera, self.starting_titers, sera_details = \
                self._get_sera(keyfile)
        self.viruses, virus_details = self._get_viruses(keyfile)

        self.dilutions = {}
        for titer in self.starting_titers:
            self._get_dilutions(titer)

        self.data = {
            'show_fit': True,
            'blank_correction': True,
            'x_axis_type': 'log',
            'curr_function' : 'logistic4',
            'experiments': self._get_all_experiments(datafile),
            'sera': sera_details,
            'viruses': virus_details,
        }

    def _get_sera(self, keyfile):
        df = pd.read_excel(keyfile, sheet_name='Sera')
        return list(df['Sera ID']), list(df['Starting titer']), \
                df.to_dict('index')

    def _get_viruses(self, keyfile):
        df = pd.read_excel(keyfile, sheet_name='Viruses')
        return [f"{row['ID']} {row['Strain name']}"
                for index, row in df.iterrows()], \
                df.to_dict('index')

    def _get_dilutions(self, start_titer):
        if start_titer not in self.dilutions:
            self.dilutions[start_titer] = [
                    1/(start_titer * pow(2, i)) for i in range(11)]
            # set the no-sera concentration to three logs below the
            # actual last dilution
            self.dilutions[start_titer][-1] = \
                    self.dilutions[start_titer][-1] / 4

    def _get_all_experiments(self, datafile):
        # override this function
        return {}

    def __call__(self):
        return self.data


class HintCx5Parser(HintBase, ParserRegistry):
    name = 'hint_cx5'
    description = 'MET CX5 HINT parser'

    def _get_all_experiments(self, datafile):
        experiments = {}
        df = pd.read_csv(datafile)

        # Reshape our data to 12-long rows, and capture the last column
        # as per-plate averaged background
        grid, background = np.split(np.reshape(
                df['SelectedObjectCount'].to_numpy(),
                (-1, 12)), [11], axis=1)
        grid = grid.astype('float64')
        mean_background = np.mean(np.reshape(background, (-1, 8)), axis=1)

        new_exp = {
            'x_axis_label': 'Dilution (conc)',
            'y_axis_label': 'Infected Cells (count)',
            'data': {},
            'results': {
                'logistic3': {},
                'logistic4': {}
            }
        }

        v_count = len(self.viruses)
        for s_index, (titer, serum) in enumerate(
                zip(self.starting_titers, self.sera)):
            for v_index, (virus, row) in \
                    enumerate(zip(self.viruses,
                        grid[v_count*s_index:v_count*(s_index+1)])):
                cc = mean_background[(v_count*s_index+v_index)//8]
                vc = row[10] - cc

                exp = experiments.get(virus, new_exp.copy())
                y_corrected = list(row - cc)
                exp['data'][serum] = {
                    'x_values': self.dilutions[titer],
                    'y_values': list(row),
                    'y_corrected': y_corrected,
                }
                experiments[virus] = exp

                x_fit = self.dilutions[titer].copy()
                x_fit[-1] = 0
                for plugin_name in exp['results'].keys():
                    labels = fit(plugin_name, x_fit, y_corrected)
                    labels['cc'] = str(cc)
                    labels['vc'] = str(vc)
                    exp['results'][plugin_name][serum] = labels

        return experiments
