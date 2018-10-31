#!/usr/bin/env python
# file StandardImport.py
from jaspr.model import JasprModel
import pandas as pd
import csv

"""
This module will load a standard 8 sample experiment from a csv or xlsx file.

File formats:
Well_plate:

1 or mor 8-row by 12-col tables representing 96 well plates
1 96 well plate per drug, seperated by a space
1 row per sample (sample names specified in the cooresponding key file)
11 dilutions (1 per column) and the last column containing the blank readings.

Key file:
"Drugs (listed in order)"
"Drug 1"
"Drug 2"
"etc..."
(1 drug for each plate in the sample file)

"ID,Strain Name (optional)"
"Strain Name 1"
"Strain Name 2"
"""

class StandardImport_CSV(object):
    """Standard Import Class

        # TODO: Modify this class to conform with plugin architecture
    """
    def __init__(self, dilutionValues, model):
        """Initialize class

            Args:
                dilutionValues: an array of dilution values, should be 11 elements
                in size.
                model: a jasprModel object to load the information into
        """
        if(len(dilutionValues) != 11):
            raise ValueError("dilutionValues must be array of",
                                            "11 values")
        self._dilutionValues = dilutionValues
        self._model = model
        self._drugs = []
        self._ids = []
        self._rawData = None

    def loadPlate(self, plateFile, keyFile):
        """Load a plate file with experiment data into the object model
            todo:
                * build this as a plug in when james code is merged
                * Perhaps add the ability to put the key file in the first
                  tab of the excel file or something like that?

            Args:
                plateFile: file location of either a csv or excel file(expecting
                           only 1 tab)
                keyFile: file location for a text file with the keys for this
                         experiement
            Returns:
                True if successful, False otherwise.
        """
        #start with loading key file for sample and drug names
        self._ids, self._drugs = self.read_keyFile(keyFile)
        #then load the raw data into a dataframe
        self._rawData = self.read_plateFile(plateFile)
        firstCols = [(drug,id) for drug in self._drugs for id in self._ids]
        self.addDrugs(firstCols)
        self.addSamples(firstCols)
        self._rawData.index = range(len(self._rawData.index ))
        self._model.clearExperiments()
        for drug in self._rawData.drug.unique():
            #Todo: have james weigh in on what the axis labels should be
            self._model.addExperiment(drug,"concentration","dilutions")
        for index,row in self._rawData.iterrows():
            results=[row.d1,row.d2,row.d3,row.d4,row.d5,row.d6, row.d7,
                     row.d8,row.d9,row.d10,row.d11]
            self._model.addDataSeries(row.drug,row.id,
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

    def read_plateFile(self, platefile):
        "read the plate file into a dataframe"
        colLabels = ['d1','d2','d3','d4','d5','d6','d7',
                     'd8','d9','d10','d11','blank']
        df = pd.read_csv(platefile,delimiter = ',',
                         names=colLabels,
                         usecols = colLabels)
        #return all rows that have data
        df = df.dropna(thresh=1)
        return df

    def read_keyFile(self, keyfile_name):
        """Read in a design file describing the experiment"""
        # read in the csv keyfile
        drugs=list()
        ids=list()
        with open(keyfile_name, 'rt') as keyfile_handle:
            rows = [row for row in csv.reader(keyfile_handle)][1:]

        #collect the drugs until we hit the sample list
        state = 'drug_list'
        for row in rows:
            if state == 'drug_list':
                if not row or row[0].strip() == '':
                    continue
                if row[0].startswith('ID'):
                    state = 'sample_list'
                    continue
                else:
                    drugs.append(row[0].strip())
            #then collect the samples
            elif state == 'sample_list':
                if not row or row[0].strip() == '':
                    continue
                elif len(row) < 2:
                    row.append('')
                if row[0].lower().strip() == 'blank':
                    ids.append(('', ''))
                else:
                    ids.append((row[0].strip(), row[1].strip(), ))
        #return the resulting lists
        return ids, drugs
