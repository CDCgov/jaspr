#!/usr/bin/env python
# file testmodel.py
import unittest
from Model import JasprModel

class TestDefaultModel(unittest.TestCase):

    def setUp(self):
        self.model = JasprModel()
        self.model.loadDefaultSession()

    def test_ConfigSetting_Retrieve(self):
        self.assertEqual(self.model.getConfigSetting("fitType"),"linear/future")

    def test_ConfigSettings_Retrieve_List(self):
        self.assertEqual(self.model.getConfigSettings(),["fitType"])

    def test_Experiments_Retrieve_List(self):
        self.assertEqual(self.model.getExperimentNames(),["Anscombe"])

    def test_Experiments_Retrieve_Labels(self):
            self.assertEqual(self.model.getExperimentLabels("Anscombe"),["X","Y"])

    def test_Experiments_Retrieve_SampleList(self):
        self.assertEqual(self.model.getSampleNames("Anscombe"),["Set I","Set II","Set III","Set IV"])

    def test_Experiments_Retrieve_SampleValues(self):
        dVal,indVal = self.model.getSampleDataSeries("Anscombe","Set IV")
        self.assertEqual(dVal,[8,8,8,8,8,8,8,19,8,8,8])
        self.assertEqual(indVal,[6.58,5.76,7.71,8.84,8.47,7.04,5.25,12.5,5.56,7.91,6.89])

unittest.main()
