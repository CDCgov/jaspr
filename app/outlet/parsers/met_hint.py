#!/usr/bin/env python

# python imports
import copy
import pandas as pd
import math
import numpy as np
from zipfile import ZipFile
import pprint
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
        return [f"{row[0]} {row['Strain']}"
                for index, row in df.iterrows()], \
                df.to_dict('index')

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


class HintCx5Parser(HintBase, ParserRegistry):
    name = 'hint_cx5'
    description = 'CX5 HINT parser'

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


class HintCeligoParser(HintCx5Parser):
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


class ICPCeligoParser(HintCx5Parser):
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
        
        mean_background = np.mean(np.reshape(background, (-1, 12)), axis=1)
        #print("background:")
        #pprint.pprint(background)
        #print("mean_background:")
        #pprint.pprint(mean_background)    
        
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
        v_count = len(self.viruses)

        #print("v_count:")
        #pprint.pprint(v_count)
        
        s_count = 1
        
        print("s_count:")
        pprint.pprint(s_count)

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

        #print("labels:")
        #pprint.pprint(exp['data'])
        
        #SeraLabels = exp['data']
        #SeraLabels.clear()
        #print("SeraLabels")
        #pprint.pprint(SeraLabels)

        return experiments

    def _get_dilutions(self, start_titer):
        if start_titer not in self.dilutions:
            self.dilutions[start_titer] = ([9.38615981661735E-08, 9.47148854222296e-07, 9.557592983515896e-06,\
            9.64448019245695e-05, 0.0009732157285115649, 0.009820631442253064, 0.0990990990990991])            
        
            self.dilutions[start_titer][-1] = \
                    self.dilutions[start_titer][-1] 

            #print("self.dilutions[start_titer]")
            #pprint.pprint(self.dilutions[start_titer])
            #print("self.dilutions")
            #pprint.pprint(self.dilutions)
            #print("[start_titer]")
            #pprint.pprint(start_titer)    
#---

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

            #print("plates:")
            #pprint.pprint(plates)
            #print("data:")
            #pprint.pprint(data)

            #print("First Check....")

        ICPplates = []
        with ZipFile(ICPdatafile, 'r') as zf_handle:
            for plate_name in sorted(
                    [name for name in zf_handle.namelist()
                    if name.endswith('.csv')]):
                df = pd.read_csv(zf_handle.open(plate_name),
                        skiprows=self.skiprows, index_col=None, nrows=8,
                        usecols=range(1, 13), header=None, dtype=np.float64)
                df_trans = pd.DataFrame.transpose(df)
                #print("df_trans:")
                #pprint.pprint(df_trans)

                ICPplates.append(df_trans)

            # data_ICP = np.split(np.reshape(pd.concat(ICPplates,
            # ignore_index=True).to_numpy(), (-1, 8)), [7], axis=1)

            # sample_data = pd.DataFrame.from_dict(sample_data)
            # sample_data.sort_values(by=['x_fit'], ascending=False)

            # print("sample_data:")
            # pprint.pprint(sample_data)    
            # print("sample_data[0]:")
            # pprint.pprint(sample_data['x_fit']) 

            data_ICP = np.split(np.reshape(pd.concat(ICPplates,
            ignore_index=True).to_numpy(), (-1, 8)), [7], axis=1)
            
            sort_index = np.array([6, 5, 4, 3, 2, 1, 0])
         

            
            data_ICP[0] = data_ICP[0][:,sort_index]
            
            #print("data_ICP([0]):")
            #pprint.pprint(data_ICP[0])

            #print("data_ICP([1]):")
            #pprint.pprint(data_ICP[1])

            #print("data_ICP:")
            #pprint.pprint(data_ICP)
            
            #print("data_ICP:")
            #pprint.pprint(data_ICP)

            return data_ICP

