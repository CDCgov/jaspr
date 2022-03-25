#!/usr/bin/env python

# python imports
import copy
from random import sample
from re import X
from tkinter import Y
from tracemalloc import stop
import pandas as pd
import math
import numpy as np
from zipfile import ZipFile
import pprint
import scipy
from scipy import stats, mean
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
        return grid, background, df

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


class FRNT_VSS(HintCx5Parser):
    name = 'FRNT V-S-S'
    description = 'FRNT V-S-S parser'
    skiprows = 1

    def __init__(self, keyfile, datafile):
        self.sera, self.dilution_factors, self.starting_titers, self.Xdata, sera_details = \
                self._get_sera(keyfile)
        self.viruses, virus_details = self._get_viruses(keyfile)

        self.dilutions = {}

        for titer in self.starting_titers:
            self._get_dilutions(titer, Xdata=self.Xdata)

        self.data = {
            'show_fit': True,
            'blank_correction': False,
            'x_axis_type': 'log',
            'curr_function' : 'logistic4',
            'experiments': self._get_all_experiments(datafile),
            'sera': self.sera,
            'viruses': virus_details,
        }

        print("self.data:")
        pprint.pprint(self.data)

    def _get_sera(self, keyfile):
        df = pd.read_excel(keyfile, sheet_name='Sera')
        
        seraNames = [f"{row[0]} {row['CUID']}" 
                    for index, row in df.iterrows()]
        seraLabels = seraNames

        seraNames = pd.DataFrame(seraNames)
        pprint.pprint("seraNames:")
        pprint.pprint(seraNames)
        
        seraCount = len(seraNames)

        AllReplicates = pd.DataFrame()
        sRow = seraCount
        sReplicate = seraCount - sRow

        while sReplicate < sRow:
            seraReplicates = {'0':[[(seraNames.iat[sReplicate,0] + " Rep1")],
                                [(seraNames.iat[sReplicate,0] + " Rep2")],
                                [(seraNames.iat[sReplicate,0] + " Rep3")],
                                [(seraNames.iat[sReplicate,0] + " Rep4")],
                                [(seraNames.iat[sReplicate,0] + " Rep5")],
                                [(seraNames.iat[sReplicate,0] + " Rep6")]]}

            seraReplicates = pd.DataFrame(seraReplicates)

            AllReplicates = AllReplicates.append(seraReplicates)
            seraList = pd.DataFrame(AllReplicates)

            sReplicate = sReplicate + 1
            if sReplicate == sRow:
                break
            sera = AllReplicates
        
        seraList.reset_index(inplace=True)
        pprint.pprint(seraList)
        seraList = seraList.drop('index', 1)
        # seraList['index'] = 0
        seraList.set_index('0')
        pprint.pprint(seraList)
        seraList = seraList.T
        seraList = pd.DataFrame(seraList)
        print(seraList.dtypes)
        pprint.pprint(seraList)
        
        Xdata = [list(df['Starting Dilution']), list(df['Dilution Factor'])]
        pprint.pprint("Xdata")
        pprint.pprint(Xdata)
  
        Starting_dilution = list(df['Starting Dilution'])
        # pprint.pprint(Starting_dilution)

        res = [ele for ele in Starting_dilution for i in range(6)]
        pprint.pprint("res")
        pprint.pprint(res)

        return seraLabels, list(df['Dilution Factor']), list(df['Starting Dilution']), Xdata, \
        df.to_dict('index')

    def _get_viruses(self, keyfile):
        df = pd.read_excel(keyfile, sheet_name='Viruses')
        
        return [f"{row[0]} {row['CUID']}" 
                        for index, row in df.iterrows()], \
                        df.to_dict('index')

    def _get_dilutions(self, start_titer, Xdata):

        with pd.option_context('display.max_rows', None, 
                            'display.max_columns', None, 
                            'display.precision', 0,):
            pprint.pprint("Xdata--Beginning")
            pprint.pprint(Xdata)
        

        X_data = pd.DataFrame(Xdata)

        pprint.pprint("self.dilutions:")
        pprint.pprint(self.dilutions)
        Sera = (len(self.dilutions))
        col = Sera
        start_dilution = X_data.iat[0, col]
        dilution_factor = X_data.iat[1, col]
        pprint.pprint("self.starting_titers")
        pprint.pprint(self.starting_titers)

        if start_titer not in self.dilutions:
            self.dilutions[start_titer] = ([start_dilution, start_dilution/dilution_factor, \
                start_dilution/dilution_factor/dilution_factor, start_dilution/dilution_factor/dilution_factor/dilution_factor, \
                start_dilution/dilution_factor/dilution_factor/dilution_factor/dilution_factor, \
                start_dilution/dilution_factor/dilution_factor/dilution_factor/dilution_factor/dilution_factor, \
                start_dilution/dilution_factor/dilution_factor/dilution_factor/dilution_factor/dilution_factor/dilution_factor,
                start_dilution/dilution_factor/dilution_factor/dilution_factor/dilution_factor/dilution_factor/dilution_factor/dilution_factor])

        pprint.pprint("self.dilutions[start_titer]")
        pprint.pprint(self.dilutions[start_titer])

    def _parse_csv(self, datafile):
        df = pd.read_csv(datafile)
        with pd.option_context('display.max_rows', None, 
                                'display.max_columns', None, 
                                'display.precision', 0,):
            pprint.pprint("df:")
            pprint.pprint(df)

        VSS = df.groupby(["Plate"], as_index=False)

        RAWdata = pd.DataFrame(VSS.groups.keys())
        pprint.pprint("Number of plates =")
        N = len(RAWdata)
        # pprint.pprint("N= ")
        print("N= ", N)
        pprint.pprint("plates:")
        print(RAWdata)
        SEMs = np.empty([1,11])
        gmeans = np.empty([1,11])
        Ameans = np.empty([1,11])
        AllData = pd.DataFrame(columns=['','','','','','','','',''])
        AllData = AllData.to_numpy()
        pprint.pprint("AllData:")
        pprint.pprint(AllData)

        Y = N
        X = N - Y
        while X <= (N-1):

            # print("Plate", RAWdata.loc[X][0])
            Temp_plate = VSS.get_group(RAWdata.loc[X][0])
            print("Temp_plate=", Temp_plate)
            Temp_plate = Temp_plate.drop('Plate', 1)
            Temp_plate = Temp_plate.drop('Well', 1)
            Temp_plate = Temp_plate.drop('Row', 1)
            Temp_plate = Temp_plate.drop('Column', 1)
            Temp_plate = Temp_plate.drop('SpotTotalAreaCh2', 1)
            print("Temp_plate before numpy=", Temp_plate)
            Temp_plate = Temp_plate.to_numpy()
            print("Temp_plate after numpy=", Temp_plate)
            
            Plate_name = RAWdata.loc[X][0]
            pprint.pprint("Plate_name:")
            pprint.pprint(Plate_name)
            print(type(Plate_name))

            VirA = Plate_name[0:4]          
            SerA = Plate_name[4:7]
            SerB = Plate_name[8:11]
            VirA_SerA = VirA + SerA
            VirA_SerB = VirA + SerB
            pprint.pprint('VirA_SerA----')
            pprint.pprint(VirA_SerA)
            pprint.pprint('VirA_SerB----')
            pprint.pprint(VirA_SerB)


            Samples = ([VirA_SerA],[VirA_SerA],[VirA_SerA],[VirA_SerA],[VirA_SerA],[VirA_SerA], \
                       [VirA_SerB],[VirA_SerB],[VirA_SerB],[VirA_SerB],[VirA_SerB],[VirA_SerB] )
            pprint.pprint("Samples:")
            pprint.pprint(Samples)

            Samples_mean =(VirA_SerA, VirA_SerB) 
            Viruses_mean =(VirA, VirA)
            Seras_mean =(SerA, SerB)
            
            print("Temp_plate before reshape=", Temp_plate)
            Temp_plate = Temp_plate.reshape(8,12)
            print("Temp_plate=", Temp_plate)

            data = np.array(np.transpose(Temp_plate))
            data = np.append(Samples, data, axis=1)
            print("data=", data)

            AllData = np.vstack ((AllData, data))
            pprint.pprint("AllData:")
            pprint.pprint(AllData)

##-- calculate arithmatic means for 6 replicates \/ \/ \/ \/
            Amean1a = mean([Temp_plate[0,0], Temp_plate[0,1], \
                            Temp_plate[0,2], Temp_plate[0,3], Temp_plate[0,4], Temp_plate[0,5]])
            Amean2a = mean([Temp_plate[1,0], Temp_plate[1,1], \
                            Temp_plate[1,2], Temp_plate[1,3], Temp_plate[1,4], Temp_plate[1,5]])
            Amean3a = mean([Temp_plate[2,0], Temp_plate[2,1], \
                            Temp_plate[2,2], Temp_plate[2,3], Temp_plate[2,4], Temp_plate[2,5]])
            Amean4a = mean([Temp_plate[3,0], Temp_plate[3,1], \
                            Temp_plate[3,2], Temp_plate[3,3], Temp_plate[3,4], Temp_plate[3,5]])
            Amean5a = mean([Temp_plate[4,0], Temp_plate[4,1], \
                            Temp_plate[4,2], Temp_plate[4,3], Temp_plate[4,4], Temp_plate[4,5]])
            Amean6a = mean([Temp_plate[5,0], Temp_plate[5,1], \
                            Temp_plate[5,2], Temp_plate[5,3], Temp_plate[5,4], Temp_plate[5,5]])
            Amean7a = mean([Temp_plate[6,0], Temp_plate[6,1], \
                            Temp_plate[6,2], Temp_plate[6,3], Temp_plate[6,4], Temp_plate[6,5]])
            Amean8a = mean([Temp_plate[7,0], Temp_plate[7,1], \
                            Temp_plate[7,2], Temp_plate[7,3], Temp_plate[7,4], Temp_plate[7,5]])                
            Amean1b = mean([Temp_plate[0,6], Temp_plate[0,7], \
                            Temp_plate[0,8], Temp_plate[0,9], Temp_plate[0,10], Temp_plate[0,11]])
            Amean2b = mean([Temp_plate[1,6], Temp_plate[1,7], \
                            Temp_plate[1,8], Temp_plate[1,9], Temp_plate[1,10], Temp_plate[1,11]])
            Amean3b = mean([Temp_plate[2,6], Temp_plate[2,7], \
                            Temp_plate[2,8], Temp_plate[2,9], Temp_plate[2,10], Temp_plate[2,11]])
            Amean4b = mean([Temp_plate[3,6], Temp_plate[3,7], \
                            Temp_plate[3,8], Temp_plate[3,9], Temp_plate[3,10], Temp_plate[3,11]])
            Amean5b = mean([Temp_plate[4,6], Temp_plate[4,7], \
                            Temp_plate[4,8], Temp_plate[4,9], Temp_plate[4,10], Temp_plate[4,11]])
            Amean6b = mean([Temp_plate[5,6], Temp_plate[5,7], \
                            Temp_plate[5,8], Temp_plate[5,9], Temp_plate[5,10], Temp_plate[5,11]])
            Amean7b = mean([Temp_plate[6,6], Temp_plate[6,7], \
                            Temp_plate[6,8], Temp_plate[6,9], Temp_plate[6,10], Temp_plate[6,11]])
            Amean8b = mean([Temp_plate[7,6], Temp_plate[7,7], \
                            Temp_plate[7,8], Temp_plate[7,9], Temp_plate[7,10], Temp_plate[7,11]])         
            AmeansA = np.array([Samples_mean[0],Viruses_mean[0], Seras_mean[0], Amean1a,Amean2a,Amean3a,Amean4a,Amean5a,Amean6a,Amean7a,Amean8a], ndmin=2)
            AmeansB = np.array([Samples_mean[1],Viruses_mean[1], Seras_mean[1], Amean1b,Amean2b,Amean3b,Amean4b,Amean5b,Amean6b,Amean7b,Amean8b], ndmin=2)
            Ameans = np.append(Ameans, AmeansA, axis=0)
            Ameans = np.append(Ameans, AmeansB, axis=0)
##-- calculate arithmatic means for 6 replicates /\ /\ /\ /\  
##-- calculate standard error of the means for 6 replicates \/ \/ \/ \/
            SEM1a = stats.sem([Temp_plate[0,0], Temp_plate[0,1], \
                            Temp_plate[0,2], Temp_plate[0,3], Temp_plate[0,4], Temp_plate[0,5]])
            SEM2a = stats.sem([Temp_plate[1,0], Temp_plate[1,1], \
                            Temp_plate[1,2], Temp_plate[1,3], Temp_plate[1,4], Temp_plate[1,5]])
            SEM3a = stats.sem([Temp_plate[2,0], Temp_plate[2,1], \
                            Temp_plate[2,2], Temp_plate[2,3], Temp_plate[2,4], Temp_plate[2,5]])
            SEM4a = stats.sem([Temp_plate[3,0], Temp_plate[3,1], \
                            Temp_plate[3,2], Temp_plate[3,3], Temp_plate[3,4], Temp_plate[3,5]])
            SEM5a = stats.sem([Temp_plate[4,0], Temp_plate[4,1], \
                            Temp_plate[4,2], Temp_plate[4,3], Temp_plate[4,4], Temp_plate[4,5]])
            SEM6a = stats.sem([Temp_plate[5,0], Temp_plate[5,1], \
                            Temp_plate[5,2], Temp_plate[5,3], Temp_plate[5,4], Temp_plate[5,5]])
            SEM7a = stats.sem([Temp_plate[6,0], Temp_plate[6,1], \
                            Temp_plate[6,2], Temp_plate[6,3], Temp_plate[6,4], Temp_plate[6,5]])
            SEM8a = stats.sem([Temp_plate[7,0], Temp_plate[7,1], \
                            Temp_plate[7,2], Temp_plate[7,3], Temp_plate[7,4], Temp_plate[7,5]])                
            SEM1b = stats.sem([Temp_plate[0,6], Temp_plate[0,7], \
                            Temp_plate[0,8], Temp_plate[0,9], Temp_plate[0,10], Temp_plate[0,11]])
            SEM2b = stats.sem([Temp_plate[1,6], Temp_plate[1,7], \
                            Temp_plate[1,8], Temp_plate[1,9], Temp_plate[1,10], Temp_plate[1,11]])
            SEM3b = stats.sem([Temp_plate[2,6], Temp_plate[2,7], \
                            Temp_plate[2,8], Temp_plate[2,9], Temp_plate[2,10], Temp_plate[2,11]])
            SEM4b = stats.sem([Temp_plate[3,6], Temp_plate[3,7], \
                            Temp_plate[3,8], Temp_plate[3,9], Temp_plate[3,10], Temp_plate[3,11]])
            SEM5b = stats.sem([Temp_plate[4,6], Temp_plate[4,7], \
                            Temp_plate[4,8], Temp_plate[4,9], Temp_plate[4,10], Temp_plate[4,11]])
            SEM6b = stats.sem([Temp_plate[5,6], Temp_plate[5,7], \
                            Temp_plate[5,8], Temp_plate[5,9], Temp_plate[5,10], Temp_plate[5,11]])
            SEM7b = stats.sem([Temp_plate[6,6], Temp_plate[6,7], \
                            Temp_plate[6,8], Temp_plate[6,9], Temp_plate[6,10], Temp_plate[6,11]])
            SEM8b = stats.sem([Temp_plate[7,6], Temp_plate[7,7], \
                            Temp_plate[7,8], Temp_plate[7,9], Temp_plate[7,10], Temp_plate[7,11]])         
            SEMA = np.array([Samples_mean[0],Viruses_mean[0], Seras_mean[0],SEM1a,SEM2a,SEM3a,SEM4a,SEM5a,SEM6a,SEM7a,SEM8a], ndmin=2)
            SEMB = np.array([Samples_mean[1],Viruses_mean[1], Seras_mean[1],SEM1b,SEM2b,SEM3b,SEM4b,SEM5b,SEM6b,SEM7b,SEM8b], ndmin=2)
            SEMs = np.append(SEMs, SEMA, axis=0)
            SEMs = np.append(SEMs, SEMB, axis=0)
##-- calculate standard error of the means for 6 replicates /\ /\ /\ /\            
            Y = Y - 1
            X = N - Y  
        
            if X == (N+1):
                break
            All_plates = AllData
            Arith_means = Ameans
            SE_means = SEMs

        Arith_means = np.delete(Arith_means, obj=0, axis=0)
        SE_means = np.delete(SE_means, obj=0, axis=0)
        pprint.pprint("Here is all the data:")
        pprint.pprint(All_plates)
        pprint.pprint("Here are the Arith_means:")
        pprint.pprint(Arith_means)
        pprint.pprint("Here are the SE_means:")
        pprint.pprint(SE_means)


        return Arith_means, SE_means
        # return the type of data that you want to use here, and 
        # block/unblock the appropriate lines below to match
        # All_plates= All Raw, unaveraged data
        # Arith_means= Arithmetic means of 6 replicates
        # SE_means= Standard Error of the means of 6 replicates
        
    def _get_all_experiments(self, datafile):
        experiments = {}

## -- All raw data no means \/ \/ \/ \/        
        # All_plates, N = self._parse_csv(datafile)
        # pprint.pprint("All_plates:")      
        # pprint.pprint(All_plates) 
                
        # labels = np.delete(All_plates, [1,2,3,4,5,6,7,8], axis=1)
        # pprint.pprint("labels:")      
        # pprint.pprint(labels)  
        # labels = np.transpose(labels)
        # pprint.pprint("labels:")      
        # pprint.pprint(labels)  
        # labels = pd.DataFrame(labels)
        # pprint.pprint("labels:")      
        # pprint.pprint(labels)  

        # data = np.delete(All_plates, 0, axis=1)
        # data = data.astype(int)
        # data = data.tolist()

## -- All raw data no means /\ /\ /\

## -- Arith_means \/ \/ \/ \/        
        Arith_means, SE_means = self._parse_csv(datafile)
        pprint.pprint("Arith_means:")      
        pprint.pprint(Arith_means)
        labels = np.delete(Arith_means, [1,2,3,4,5,6,7,8, 9, 10], axis=1)
        labels = pd.DataFrame(labels)
        pprint.pprint("labels are here ---------------")
        pprint.pprint(labels)
        data = np.delete(Arith_means, 0, axis=1)
        pprint.pprint("data")
        pprint.pprint(data)
        # data = data[np.argsort(data[:,0])]
        # pprint.pprint("data_sorted-[:,0]")
        # pprint.pprint(data)
        ind = np.lexsort((data[:,0],data[:,1]))
        pprint.pprint("data_sorted-[:,0],[:,1]")
        pprint.pprint(data[ind])
        data = data[ind]
        data = np.delete(data, 0, axis=1)
        data = np.delete(data, 0, axis=1)
        pprint.pprint("Data type: data")
        pprint.pprint(data.dtype)
        data = pd.DataFrame(data)
        pprint.pprint("data")
        pprint.pprint(data)
        data= data.astype(float)
        data = pd.DataFrame.to_numpy(data)
        pprint.pprint("data")
        pprint.pprint(data)
        pprint.pprint("Arith_means:")      
        pprint.pprint(Arith_means) 
## -- Arith_means /\ /\ /\

## -- SE_means \/ \/ \/
        pprint.pprint("SE_means:")      
        pprint.pprint(SE_means)      

        error = np.delete(SE_means, 0, axis=1)
        pprint.pprint("error")
        pprint.pprint(error)
        # error = error[np.argsort(error[:,0])]
        # pprint.pprint("error_sorted-[:,0]")
        # pprint.pprint(error)
        ind = np.lexsort((error[:,0],error[:,1]))
        pprint.pprint("error_sorted-[:,0],[:,1]")
        pprint.pprint(error[ind])
        error = error[ind]
        error = np.delete(error, 0, axis=1)
        error = np.delete(error, 0, axis=1)
        pprint.pprint("data type: error")
        pprint.pprint(error.dtype)
        error = pd.DataFrame(error)
        pprint.pprint("error")
        pprint.pprint(error)
        error= error.astype(float)
        error = pd.DataFrame.to_numpy(error)
        pprint.pprint("error")
        pprint.pprint(error)
        pprint.pprint("Arith_means:")      
        pprint.pprint(Arith_means)   
## -- SE_means /\ /\ /\

        pprint.pprint("labels:")      
        pprint.pprint(labels)  
        pprint.pprint("data:")      
        pprint.pprint(data)                 

        new_exp = {
            'x_axis_label': 'Relative Dilution (ppm)',
            'y_axis_label': 'Infected Cell Population (ICP)',
            'data': {},
            'results': {
                'logistic3': {},
                'robust_logistic3': {},
                'logistic4': {},
                'robust_logistic4': {}
            }
        }

        # viruses per plate = 1       
        print("self.sera:")
        pprint.pprint(self.sera)
        with pd.option_context('display.max_rows', None, 
                                 'display.max_columns', None, 
                                 'display.precision', 0,):
            pprint.pprint("self.sera:")
            pprint.pprint(self.sera)

        v_count = len(self.viruses)
        vpp = 1

        print("self.viruses:")
        pprint.pprint(self.viruses)
        with pd.option_context('display.max_rows', None, 
                                 'display.max_columns', None, 
                                 'display.precision', 0,):
            pprint.pprint("self.viruses:")
            pprint.pprint(self.viruses)

        print("v_count:")
        pprint.pprint(v_count)
        
        s_count = len(self.sera)
        
        print("s_count:")
        pprint.pprint(s_count)

        data_count = len(data)
        pprint.pprint("data_count:")
        pprint.pprint(data_count)
        X=0

        pprint.pprint("data")
        pprint.pprint(data)
# - - - OG \/ \/ \/
        while X < data_count:
            for s_index, (titer, serum) in enumerate(
                zip(self.starting_titers, self.sera)):
                for v_index, virus in enumerate(self.viruses):
                # find the plate and position of a sample
                    # plate_offset, position_offset = divmod(v_index, v_count)
                    # pprint.pprint(divmod(v_index, v_count))
                    row = data[X]
                    StandardError = error[X]
                    # pprint.pprint("v_index:")
                    # pprint.pprint(v_index)          

                    # pprint.pprint("virus")
                    # pprint.pprint(virus)

                    # pprint.pprint("vpp")
                    # pprint.pprint(vpp)

                    # pprint.pprint("s_count:")
                    # pprint.pprint(s_count)

                    # pprint.pprint("position_offset:")
                    # pprint.pprint(position_offset)
                
                    # pprint.pprint("plate_offset:")
                    # pprint.pprint(plate_offset)
                    print('X= ', X)
                    pprint.pprint("row")
                    pprint.pprint(row)
                    pprint.pprint("StandardError")
                    pprint.pprint(StandardError)
                    pprint.pprint(virus)
                    pprint.pprint(serum)
                    exp = experiments.get(virus, copy.deepcopy(new_exp))
                    y_corrected = list(row)
                    x_fit = self.dilutions[titer].copy()
                    x_fit[-1] = 0

                    exp['data'][serum] = {
                        'x_values': self.dilutions[titer],
                        'x_fit': x_fit,
                        'y_values': list(row),
                        'y_error': list(StandardError),
                    }
                    X= X+1
                    experiments[virus] = exp              

                    for plugin_name in exp['results'].keys():
                        try:
                            labels = fit(plugin_name, x_fit, y_corrected)
                        except ValueError:
                            labels = {plugin_name: 'regression failed'}
                    
                        exp['results'][plugin_name][serum] = labels

                    if X == (data_count):
                        break
                    pprint.pprint("done...")                

        return experiments