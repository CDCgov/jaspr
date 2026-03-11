#!/usr/bin/env python
# file met_2xdilutions_8samples.py

"""Load an MET 8 sample experiment from a csv or xlsx file.

    Assumes 2 fold dilutions

    File formats:
        Well_plate:
          * 1 or mor 8-row by 12-col tables representing 96 well plates
          * 1 96-well plate per drug, seperated by a blank row
          * 1 row per sample (sample names specified in the key file)
          * 11 dilutions (1 per column)
          * Last column contains blanks

    Key file:
        "Drugs (listed in order)", "Starting Dilution"
        "Drug 1","40"
        "Drug 2","80"
        ...

        "ID","Strain Name (optional)"
        "Strain Name 1"
        "Strain Name 2"

"""
## Code blocked August 2022 to clean up JASPR for FRNT production:

# # python imports
# import pandas as pd
# import csv
# from itertools import product

# # app imports
# from outlet import ParserRegistry


# class ParseMET8Sample(ParserRegistry):
#     name = 'met8sample'
#     description = 'MET 8 samples per plate, 2-fold dilutions'

#     #def __init__(self, keyfile, datafile):
#     #    self.sera, self.starting_titers = self._get_sera(keyfile)
#     #    self.titer_lookup = dict(zip(self.sera, serlf.starting_titers))
#     #    self.viruses = self._get_viruses(keyfile)

#     #    self.dilutions = {}
#     #    for titer in self.starting_titers:
#     #        self._get_dilutions(titer)

#     #    self.data = {
#     #        'show_fit': True,
#     #        'blank_correction': True,
#     #        'x_axis_type': 'log',
#     #        'curr_function' : 'logistic3',
#     #    }

#     #    self.data['experiments'] = self._get_experiments(datafile)

#     #def _get_sera(self, keyfile):
#     #    df = read_excel(keyfile, sheet_name='Sera')
#     #    return list(df['Sera']), list(df['Starting titer'])

#     #def _get_viruses(self, keyfile):
#     #    df = read_excel(keyfile, sheet_name='Viruses')
#     #    return [f"{row['ID']} {row['Strain Name (optional)']}"
#     #            for index, row in df.iterrows()]

#     #def _get_dilutions(self, start_titer):
#     #    if start_titer not in self.dilutions:
#     #        self.dilutions[start_titer] = [
#     #                1/(start_titer * pow(2, i)) for i in range(12)]
#     #        self.dilutions[start_titer][-1] = \
#     #                self.dilutions[start_titer][-1] / 8

#     #def _get_experiments(self, datafile):
#     #    df = read_excel(datafile)
#     #    df.dropna(inplace=True)
#     #    experiments = {}
#     #    for index, (serum, virus) in \
#     #            enumerate(product(self.sera, self.viruses)):
#     #        titer = self.titer_lookup[serum])
#     #        exp = experiments.get(virus, {
#     #                'x_axis_label': 'Dilution (conc)',
#     #                'y_axis_label': 'Fluorescence (A.U.)'
#     #        })
#     #        data = {
#     #            'x_values': self.dilutions[titer],
#     #            'y_values'
#     #        }

#     #    return exps

#     def __call__(self):
#         return self.data
