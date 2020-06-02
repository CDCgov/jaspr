#!/usr/bin/env python

# python imports
import itertools
from collections import OrderedDict

import pandas as pd
import numpy as np

from io import StringIO
from zipfile import ZipFile

# jaspr imports
from outlet import ParserRegistry


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
            'curr_function' : 'logistic3',
            'experiments': self._get_all_experiments(datafile),
            'sera': sera_details,
            'viruses': virus_details,
        }

    def _get_sera(self, keyfile):
        df = pd.read_excel(keyfile, sheet_name='Sera')
        return list(df['Sera']), list(df['Starting titer']), \
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
            self.dilutions[start_titer][-1] = 0

    def _get_all_experiments(self, datafile):
        experiments = {}
        df = pd.read_csv('data')

        # Reshape our date to 12-long rows, and capture the last column
        # as per-plate averaged background
        grid, background = np.split(np.reshape(
                df['SelectedObjectCount'].to_numpy(), (-1, 12)), [11], axis=1)
        mean_background = np.mean(np.reshape(background, (-1, 8)), axis=1)

        v_count = len(self.viruses)
        for s_index, serum in enumerate(self.sera):
            for v_index, (virus, titer, row) in enumerate(
                    zip(self.viruses, self.starting_titers,
                    grid[v_count*s_index:v_count*(s_index+1)])):
                cc = background[(v_count*s_index+v_index)//8]
                vc = row[10] - cc

                exp = experiments.get(virus, {
                    'x_axis_label': 'Dilution (conc)',
                    'y_axis_label': 'Infected Cells (count)',
                    'data': {},
                    'cc': cc,
                    'vc': vc,
                })
                exp['data'][serum] = {
                    'x_values': self.dilutions[titer],
                    'y_values': list(row),
                    'y_corrected': list(row - cc),
                    'cc': cc,
                }

                experiments[virus] = exp

        return experiments

    def __call__(self):
        return self.data


class HintCx5Parser(HintBase, ParserRegistry):
    name = 'hint_cx5'
    description = 'MET CX5 HINT parser'
