#!/usr/bin/env python

# python imports
from io import StringIO
from zipfile import ZipFile
from pandas import read_excel
from numpy import mean

# jaspr imports
from outlet import ParserRegistry


class SmallFraParser(ParserRegistry):
    name = 'small_fra'
    description = 'VRT small-format FRA parser'

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
            'curr_function' : 'logistic3',
        }

        self.data['experiments'] = self._get_experiments(datafile)

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

    def _get_experiments(self, datafile):
        raw_exps = []
        with ZipFile(datafile) as zf_handle:
            for plate_name in zf_handle.namelist():
                index = int(plate_name.split('.')[0])
                df = read_excel(zf_handle.open(plate_name),
                        skiprows=34, index_col=None, nrows=8,
                        usecols='C:N', header=None, convert_float=False)
                vc = mean(df[13][0:4])
                cc = mean(df[13][4:8])
                exp = {
                    'x_axis_label': 'Dilution (conc)',
                    'y_axis_label': 'Foci above Background (count)',
                }
                data = {}
                for label, titer, col in \
                        zip(self.sera, self.starting_titers, range(2, 13)):
                    data[label] = {
                        'x_values': self.dilutions[titer],
                        'y_values': list(df[col]),
                        'y_corrected': list(df[col] - cc),
                    }
                exp['data'] = data
                raw_exps.append((index, exp))
            raw_exps.sort()
            return dict((virus, exp)
                    for virus, (index, exp) in zip(self.viruses, raw_exps))

    def __call__(self):
        return self.data
