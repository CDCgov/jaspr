#!/usr/bin/env python
# file testmodel.py

# python imports
import unittest
import sys

# local imports
from model import JasprModel
from jaspr.model import JasprModel


class TestDefaultModel(unittest.TestCase):

    def setUp(self):
        self.model = JasprModel()
        self.model.loadDefaultModel()

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
        dVal,indVal,blankValue = self.model.getSampleDataSeries("Anscombe","Set IV")
        self.assertEqual(dVal,[8,8,8,8,8,8,8,19,8,8,8])
        self.assertEqual(indVal,[6.58,5.76,7.71,8.84,8.47,7.04,5.25,12.5,5.56,7.91,6.89])

    def testClearExperiments(self):
        self.model.clearExperiments()
        self.assertEqual(len(self.model._jasprExperiments["experiments"]), 0)

    def testAddExperiment(self):
        self.model.addExperiment("testExperiment","x","y")
        myExperiment = self.model.getExperiment("testExperiment")
        self.assertEqual(myExperiment["experimentName"],"testExperiment")

    def testAddExperiments(self):
        self.model.clearExperiments()
        self.model.addExperiment("testExperiment1","x","y")
        self.model.addExperiment("testExperiment2","x","y")
        self.assertEqual(self.model.getExperimentNames(),["testExperiment1","testExperiment2"])

    def testAddDataSeries(self):
        self.model.addExperiment("testExperiment","x","y")
        self.model.addDataSeries("testExperiment","testSample",[1,2,3,4],[5,6,7,8],0)
        self.assertEqual(self.model.getSampleNames("testExperiment"), ["testSample"])
unittest.main()
