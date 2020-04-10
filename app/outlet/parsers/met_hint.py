#!/usr/bin/env python

# python imports
from io import StringIO
from zipfile import ZipFile
from pandas import read_excel
import numpy as np

# jaspr imports
from outlet import ParserRegistry


class HintBase(object):
    """A base class for HINT parsers

    Add attributes `name` and `description` to the implementation classes

    Override _get_plate_experiments if needed

    """

    def __init__(self, keyfile, datafile):
        self.sera, self.starting_titers = self._get_sera(keyfile)
        self.viruses = self._get_viruses(keyfile)

        self.dilutions = {}
        for titer in self.starting_titers:
            self._get_dilutions(titer)

        self.data = {
            'show_fit': True,
            'blank_correction': True,
            'x_axis_type': 'log',
            'curr_function' : 'logistic4',
        }

        self.data['experiments'] = self._get_all_experiments(datafile)

    def _get_sera(self, keyfile):
        df = read_excel(keyfile, sheet_name='Sera')
        return list(df['Sera']), list(df['Starting titer'])

    def _get_viruses(self, keyfile):
        df = read_excel(keyfile, sheet_name='Viruses')
        return [f"{row['ID']} {row['Strain Name (optional)']}"
                for index, row in df.iterrows()]

    def _get_dilutions(self, start_titer):
        if start_titer not in self.dilutions:
            self.dilutions[start_titer] = [
                    1/(start_titer * pow(2, i)) for i in range(8)]

    def _get_single_experiment(self, df, control_col=11):
        cc = np.mean(df[control_col][4:8])
        vc = np.mean(df[control_col][0:4]) - cc

        exp = {
            'x_axis_label': 'Dilution (conc)',
            'y_axis_label': 'Foci above Background (count)',
            'data': {},
            'cc': cc,
            'vc': vc,
        }

        for label, titer, col in \
                zip(self.sera, self.starting_titers, range(control_col)):
            exp['data'][label] = {
                'x_values': self.dilutions[titer],
                'y_values': list(df[col]),
                'y_corrected': list(df[col] - cc),
            }

        return exp

    def _get_plate_experiments(self, index, df):
        return ((index, self._get_single_experiment(df)), )

    def _get_all_experiments(self, datafile):
        raw_exps = []
        with ZipFile(datafile) as zf_handle:
            for plate_name in zf_handle.namelist():
                index = int(plate_name.split('.')[0])
                df = read_excel(zf_handle.open(plate_name),
                        skiprows=34, index_col=None, nrows=8,
                        usecols='C:N', names=range(0,12),
                        header=None, convert_float=False)

                raw_exps.extend(self._get_plate_experiments(index, df))

        raw_exps.sort()
        return dict((virus, exp)
                for virus, (index, exp) in zip(self.viruses, raw_exps))

    def __call__(self):
        return self.data


#class LargeFraParser(FraBase, ParserRegistry):
#    name = 'large_fra'
#    description = 'VRT large-format FRA parser'
#
#
#class SmallFraParser(FraBase, ParserRegistry):
#    name = 'small_fra'
#    description = 'VRT small-format FRA parser'
#
#    def _get_plate_experiments(self, index, df):
#        # split our primary plate into two half-size plates and renumber
#        # the columns for the second one to be identical to the first
#        dfa, dfb = np.split(df, 2, axis=1)
#        dfb.columns = dfa.columns
#
#        return (
#                ((index, 'a'),
#                    self._get_single_experiment(dfa, control_col=5)),
#                ((index, 'b'),
#                    self._get_single_experiment(dfb, control_col=5)), )
