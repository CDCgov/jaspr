#!/usr/bin/env python

# python imports
import copy
from random import sample
import pandas as pd
import math
import numpy as np
from zipfile import ZipFile
import pprint
import scipy
from scipy import stats
from decimal import Decimal
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
            'curr_function' : 'robust_logistic4',
            'experiments': self._get_all_experiments(datafile),
            'sera': sera_details,
            'viruses': virus_details,
        }

    def _get_sera(self, keyfile):
        df = pd.read_excel(keyfile, sheet_name='Sera')
        return list(df['Name']), list(df['Starting titer']), \
                df.to_dict('index')
    
    def _get_viruses(self, keyfile):
        df = pd.read_excel(keyfile, sheet_name='Viruses')

        # Support historical and alternate keyfile headers.
        colmap = {str(col).strip().lower(): col for col in df.columns}

        id_col = None
        for candidate in ['id', 'virus id', 'virus', 'virus number', 'name']:
            if candidate in colmap:
                id_col = colmap[candidate]
                break
        if id_col is None:
            id_col = df.columns[0]

        strain_col = None
        for candidate in ['strain', 'strain name', 'strain name (optional)', 'variant', 'lineage']:
            if candidate in colmap:
                strain_col = colmap[candidate]
                break

        viruses = []
        for index, row in df.iterrows():
            virus_id = str(row[id_col]).strip() if not pd.isna(row[id_col]) else ''

            strain = ''
            if strain_col is not None and not pd.isna(row[strain_col]):
                strain = str(row[strain_col]).strip()

            virus_name = f"{virus_id} {strain}".strip()
            if not virus_name:
                virus_name = f"Virus {index + 1}"
            viruses.append(virus_name)

        return viruses, df.to_dict('index')

    def _get_dilutions(self, start_titer):
        if start_titer not in self.dilutions:
            self.dilutions[start_titer] = [
                    1/(start_titer * pow(2, i)) for i in range(11)]
            # set the no-sera concentration to three logs below the
            # actual last dilution
            self.dilutions[start_titer][-1] = \
                    self.dilutions[start_titer][-1] / 8

    def _get_all_experiments(self, datafile):
        # override this function
        return {}

    def __call__(self):
        return self.data


class HintCx5Base(HintBase):
    """Shared HINT/ICP parsing logic for supported instrument-specific parsers."""

    def _parse_csv(self, datafile):
        df = pd.read_csv(datafile)

        # Reshape our data to 12-long rows, and capture the last column
        # as per-plate averaged background
        grid, background = np.split(np.reshape(
                df['SelectedObjectCount'].to_numpy(),
                (-1, 12)), [11], axis=1)
        grid = grid.astype('float64')
        return grid, background

    def _get_all_experiments(self, datafile):
        experiments = {}
        grid, background = self._parse_csv(datafile)
        mean_background = np.mean(np.reshape(background, (-1, 8)), axis=1)

        new_exp = {
            'x_axis_label': 'Relative Dilution (ppm)',
            'y_axis_label': 'Infected Cell Population (ICP)',
            'data': {},
            'results': {
                'robust_logistic4': {},
            }
        }

        # viruses per plate = 8
        vpp = 8
        v_count = len(self.viruses)
        s_count = len(self.sera)

        for s_index, (titer, serum) in enumerate(
                zip(self.starting_titers, self.sera)):
            for v_index, virus in enumerate(self.viruses):
                # find the plate and position of a sample
                plate_offset, position_offset = divmod(v_index, vpp)

                row = grid[vpp * (plate_offset * s_count + s_index) \
                        + position_offset]
                cc = mean_background[(v_count*s_index+v_index)//vpp]
                vc = row[10] - cc

                exp = experiments.get(virus, copy.deepcopy(new_exp))
                #y_corrected = list(row)
                y_corrected = list(row - cc)
                x_fit = self.dilutions[titer].copy()
                x_fit[-1] = 0
                exp['data'][serum] = {
                    'x_values': self.dilutions[titer],
                    'x_fit': x_fit,
                    'y_values': list(row),
                    'y_corrected': y_corrected,
                }
                experiments[virus] = exp

                for plugin_name in exp['results'].keys():
                    try:
                        labels = fit(plugin_name, x_fit, y_corrected)
                    except ValueError:
                        labels = {plugin_name: 'regression failed'}
                    labels['cc'] = str(cc)
                    labels['vc'] = str(vc)
                    exp['results'][plugin_name][serum] = labels

        return experiments


class HintCeligoParser(HintCx5Base, ParserRegistry):
    name = 'HINT celigo'
    description = 'Celigo HINT parser'
    skiprows = 97

    def _parse_csv(self, datafile):
        plates = []
        with ZipFile(datafile, 'r') as zf_handle:
            for plate_name in sorted(
                    [name for name in zf_handle.namelist()
                    if name.endswith('.csv')]):
                df = pd.read_csv(zf_handle.open(plate_name),
                        skiprows=self.skiprows, index_col=None, nrows=8,
                        usecols=range(1, 13), header=None, dtype=np.float64)
                plates.append(df)
        return np.split(np.reshape(pd.concat(plates,
                ignore_index=True).to_numpy(), (-1, 12)), [11], axis=1)


class ICPCeligoParser(HintCx5Base, ParserRegistry):
    name = 'ICP celigo'
    description = 'Celigo ICP parser'
    skiprows = 97

    def _get_sera(self, keyfile):
        df = pd.read_excel(keyfile, sheet_name='Sera')
        ICP_sera = {'Name': ["No Sera"], 'Starting titer': ["80"]}
        print("ICP_Sera")
        pprint.pprint(ICP_sera)
        print("dataframes--")
        df = pd.DataFrame(data=ICP_sera)
        pprint.pprint(df)

        return list(df['Name']), list(df['Starting titer']), \
                df.to_dict('index')

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
            'curr_function' : 'ICP_robust_logistic3',
            'experiments': self._get_all_experiments(datafile),
            'sera': "sera_details",
            'viruses': virus_details,
        }

        print("self.data:")
        pprint.pprint(self.data)
#---
    def _parse_csv(self, ICPdatafile):
        df = pd.read_csv(ICPdatafile)
        print(df)
        # Reshape our data to 12-long rows, and capture the last column
        # as per-plate averaged background
        grid, background = np.split(np.reshape(
                df['SelectedObjectCount'].to_numpy(),
                (-1, 12)), [11], axis=1)
        grid = grid.astype('float64')

        return grid, background

    def _get_all_experiments(self, ICPdatafile):
        experiments = {}
        grid, background = self._parse_csv(ICPdatafile)
        pprint.pprint("Look here!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        pprint.pprint("grid:")
        pprint.pprint(grid)
        mean_background = np.mean(np.reshape(background, (-1, 12)), axis=1)
        print("background:")
        pprint.pprint(background)
        print("mean_background:")
        pprint.pprint(mean_background)    
        
        new_exp = {
            'x_axis_label': 'Relative Dilution (ppm)',
            'y_axis_label': 'Infected Cell Population (ICP)',
            'data': {},
            'results': {
                'ICP_robust_logistic3': {}
            }
        }

        # viruses per plate = 12
        vpp = 12
        print("self.viruses:")
        pprint.pprint(self.viruses)
        v_count = len(self.viruses)

        #print("v_count:")
        #pprint.pprint(v_count)
        
        s_count = 1
        
        print("s_count:")
        pprint.pprint(s_count)

        print("self.viruses:")
        pprint.pprint(self.viruses)
        
        print("self.sera:")
        pprint.pprint(self.sera)

        for s_index, (titer, serum) in enumerate(
                zip(self.starting_titers, self.sera)):
            for v_index, virus in enumerate(self.viruses):
                # find the plate and position of a sample
                plate_offset, position_offset = divmod(v_index, vpp)
                row = grid[vpp * (plate_offset * s_count + 0) \
                        + position_offset]
                
                cc = mean_background[(v_count* 0 +v_index)//vpp]
                vc = row[6] - cc
                
                #print("v_index:")
                #pprint.pprint(v_index)
                #print("s_index:")
                #pprint.pprint(s_index)
                #pprint.pprint(row)

                exp = experiments.get(virus, copy.deepcopy(new_exp))
                #y_corrected = list(row)
                y_corrected = list(row - cc)
                x_fit = self.dilutions[titer].copy()

                print("'x_values': self.dilutions[titer]")
                pprint.pprint(self.dilutions[titer])
                print("'x_fit': x_fit")
                pprint.pprint(x_fit)
                print("'y_values': list[row]")
                #pprint.pprint(list[row])
                print("'y_corrected': y_corrected")
                pprint.pprint(y_corrected)

                exp['data'][serum] = {
                    'x_values': self.dilutions[titer],
                    'x_fit': x_fit,
                    'y_values': list(row),
                    'y_corrected': y_corrected,
                }
                
                experiments[virus] = exp
               
                for plugin_name in exp['results'].keys():
                    try:
                        labels = fit(plugin_name, x_fit, y_corrected)
                    except ValueError:
                        labels = {plugin_name: 'regression failed'}
                    labels['cc'] = str(cc)
                    labels['vc'] = str(vc)
                    
                    exp['results'][plugin_name][serum] = labels

        return experiments

    def _get_dilutions(self, start_titer):
        if start_titer not in self.dilutions:
            self.dilutions[start_titer] = ([9.38615981661735E-08, 9.47148854222296e-07, 9.557592983515896e-06,\
            9.64448019245695e-05, 0.0009732157285115649, 0.009820631442253064, 0.0990990990990991])            
        
            self.dilutions[start_titer][-1] = \
                    self.dilutions[start_titer][-1] 

    def _parse_csv(self, ICPdatafile):
        plates = []
        with ZipFile(ICPdatafile, 'r') as zf_handle:
            for plate_name in sorted(
                    [name for name in zf_handle.namelist()
                    if name.endswith('.csv')]):
                df = pd.read_csv(zf_handle.open(plate_name),
                        skiprows=self.skiprows, index_col=None, nrows=8,
                        usecols=range(1, 13), header=None, dtype=np.float64)
                plates.append(df)

            data = np.split(np.reshape(pd.concat(plates,
                ignore_index=True).to_numpy(), (-1, 12)), [11], axis=1)

        ICPplates = []
        with ZipFile(ICPdatafile, 'r') as zf_handle:
            for plate_name in sorted(
                    [name for name in zf_handle.namelist()
                    if name.endswith('.csv')]):
                df = pd.read_csv(zf_handle.open(plate_name),
                        skiprows=self.skiprows, index_col=None, nrows=8,
                        usecols=range(1, 13), header=None, dtype=np.float64)
                df_trans = pd.DataFrame.transpose(df)

                ICPplates.append(df_trans)


            data_ICP = np.split(np.reshape(pd.concat(ICPplates,
            ignore_index=True).to_numpy(), (-1, 8)), [7], axis=1)
            
            sort_index = np.array([6, 5, 4, 3, 2, 1, 0])
         
            data_ICP[0] = data_ICP[0][:,sort_index]
            
            return data_ICP
