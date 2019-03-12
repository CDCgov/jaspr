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

# python imports
import pandas as pd
import csv

# app imports
from outlet import ParserRegistry


class ParseMET8Sample(ParserRegistry):
    name = 'met8sample'
    description = 'MET 8 samples per plate, 2-fold dilutions'

    def __init__(self, keyfile, datafile):
        self.keyfile = keyfile
        self.datafile = datafile
        #self.concs = [0] * 11
        #self.experiment_names = []
        #self.sample_names = []
        #self.raw_Data = None

    def _parse_keyfile(self):
        """Read in a design file describing the experiment"""
        with open(self.keyfile, 'rt') as handle:
            rows = [row for row in csv.reader(handle)][1:]

        # collect the experiments until we hit the sample list
        # then collect the samples
        state = 'experiments'
        experiment_names, sample_names = [], []
        for row in rows:
            if state == 'experiments':
                if not row or row[0].strip() == '':
                    continue
                elif row[0].startswith('ID'):
                    state = 'samples'
                    continue
                else:
                    experiment_names.append(row[0].strip())

            elif state == 'samples':
                if not row or row[0].strip() == '':
                    continue
                elif len(row) < 2:
                    row.append('')
                else:
                    sample_names.append((row[0].strip(), row[1].strip(), ))

        return experiment_names, sample_names

    def _parse_platefile(self, platefile):
        colLabels = ['d1','d2','d3','d4','d5','d6','d7',
                     'd8','d9','d10','d11','blank']
        df = pd.read_csv(platefile,delimiter = ',',
                         names=colLabels,
                         usecols=colLabels)
        df = df.dropna(thresh=1)
        return df

    def __call__(self):
        experiment_names, sample_names = self._parse_keyfile()
        raw_data = self._parse_platefile()
        raw_data

    def loadPlate(self, plateFile, keyFile):
        self._rawData = self.read_plateFile(plateFile)
        firstCols = [(drug,id) for drug in self._drugs for id in self._ids]
        self.addDrugs(firstCols)
        self.addSamples(firstCols)
        self._rawData.index = range(len(self._rawData.index ))
        self._model._jasprExperiments.clearExperiments()
        for drug in self._rawData.drug.unique():
            self._model._jasprExperiments.addExperiment(drug,"concentration","dilutions")
        for index,row in self._rawData.iterrows():
            results=[row.d1,row.d2,row.d3,row.d4,row.d5,row.d6, row.d7,
                     row.d8,row.d9,row.d10,row.d11]
            self._model._jasprExperiments.addDataSeries(row.drug,row.id,
                    results, self._dilutionValues, row.blank)
        return

    def addSamples(self, firstCols):
        """add the id and strains to dataframe """
        #if there id and strain in the first sample add them both
        #ToDo: add tests for the strains being only in some samples (not first)
        if isinstance(firstCols[0][1],tuple):
            self._rawData.insert(1,"id",[col[1][0] for col in firstCols])
            #add strain to the end
            self._rawData["strain"]=[col[1][1] for col in firstCols]
        else:
            self._rawData.insert(1,"id",[col[1] for col in firstCols])

    def addDrugs(self,firstCols):
        """ add the drugs to the dataframe """
        #create an array of drugs and _ids
        self._rawData.insert(0,"drug",[col[0] for col in firstCols])
        return

