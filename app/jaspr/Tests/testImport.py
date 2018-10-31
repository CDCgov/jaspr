#!/usr/bin/env python
# file testmodel.py
import unittest
import sys


from jaspr.model import JasprModel
from jaspr.standardImport import StandardImport_CSV

class TestDefaultModel(unittest.TestCase):
    dilutionValues = [2.5e-2, 1.25e-2, 6.25e-3, 3.125e-3, 1.5625e-3, 7.8125e-4,
                      3.90625e-4, 1.953125e-4, 9.765625e-5, 4.8832813e-5, 0]
    good_platefile='/app/jaspr/Tests/test_BasicImportDataFile.csv'
    good_keyfile='/app/jaspr/Tests/test_BasicImportKeyFile.txt'

    def setUp(self):
        self._model = JasprModel()
        self._model.loadDefaultModel()
        self._import = StandardImport_CSV( self.dilutionValues, self._model)

    def test_ObjectCreation(self):
        self.assertEqual(len(self._import._dilutionValues),11)

    def test_LoadKeyFile(self):
        self._import.loadPlate(self.good_platefile,self.good_keyfile)
        self.assertEqual(len(self._import._drugs),2)
        self.assertEqual(len(self._import._ids), 16)

    def test_LoadDataFile(self):
        self._import.loadPlate(self.good_platefile,self.good_keyfile)
        ''' TODO: Figure out a test that validates data file was loaded after
        implementing the import functions'''
        drugCount = len(self._import._drugs)
        sampleCount = len(self._import._ids)
        rowCount = len(self._import._rawData)
        self.assertEqual(rowCount, drugCount*sampleCount)

    def test_loadModelExperiments(self):
        self._import.loadPlate(self.good_platefile,self.good_keyfile)
        self.assertEqual(self._model.getExperimentNames(),
        ['Anti-B/Laos/0654(Ferret3)', 'Anti-B/Laos/0654(Ferret11)'])

    def testLoadModelSamples(self):
        self._import.loadPlate(self.good_platefile,self.good_keyfile)
        self.assertEqual(len(self._model.getSampleNames("Anti-B/Laos/0654(Ferret3)")), 16)

unittest.main()
