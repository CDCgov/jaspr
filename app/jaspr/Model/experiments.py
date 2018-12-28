import json
DEFAULT_EXPIREMENT = """{"experiments": [
     {"experimentName": "Anscombe",
        "dependentVariableLabel": "X",
        "independentVariableLabel": "Y",
        "dataSeries" : [
            {"sampleName":"Set I",
            "dependentValues":[10,8,13,9,11,14,6,4,12,7,5],
            "independentValues":[8.04,6.95,7.58,8.81,8.33,9.96,7.24,4.26,10.84,4.82,5.68],
            "blankValue": 0},
            {"sampleName":"Set II",
            "dependentValues":[10,8,13,9,11,14,6,4,12,7,5],
            "independentValues":[9.14,8.14,8.74,8.77,9.26,8.1,6.13,3.1,9.13,7.26,4.74],
            "blankValue": 0},
            {"sampleName":"Set III",
            "dependentValues":[10,8,13,9,11,14,6,4,12,7,5],
            "independentValues":[7.46,6.77,12.74,7.11,7.81,8.84,6.08,5.39,8.15,6.42,5.73],
            "blankValue": 0},
            {"sampleName":"Set IV",
            "dependentValues":[8,8,8,8,8,8,8,19,8,8,8],
            "independentValues":[6.58,5.76,7.71,8.84,8.47,7.04,5.25,12.5,5.56,7.91,6.89],
            "blankValue": 0 }
        ]}
    ]}"""
class Experiments(object):
    """
    This is the model to handle the data for the experiements.  The
    information stored is as follows:
        {"expirements": [
            {"experimentName": "experiment name",
                "dependentVariableLabel": "dependent axis label",
                "independentVariableLabel": "independent axis label",
                "dataSeries" : [
                    {"sampleName":"sampleNameValue",
                    "dependentValues":[depValue1, depValue2,depValue3],
                    "independentValues":[indValue1, indValue3, indValue3],
                    "blankValue": blankValue
                    }
                ]}
            }
        ]}
    """
    def __init__(self):
        """ initialize with empty data
        """
        self._jasprExperiments = {"experiments": []}

    def addExperiment(self, name, xLabel, yLabel):
        """ add a new experiment to the list """
        self._jasprExperiments["experiments"].append(
                    {"experimentName": name,
                    "dependentVariableLabel": yLabel,
                    "independentVariableLabel": xLabel,
                    "dataSeries" : []})

    def addDataSeries(self, experimentKey, sampleName,
                            dependentValues, independentValues,
                            blankValue):
        """ add a samples to an experiement """
        self.getExperiment(experimentKey)["dataSeries"].append(
                {"sampleName": sampleName,
                "dependentValues":dependentValues,
                "independentValues":independentValues,
                "blankValue": blankValue
                })

    def clearExperiments(self):
        """clear the experiements section of the document."""
        self._jasprExperiments["experiments"] = []

    def loadDefaultModel(self):
        """Loads the model with UI State settings
        Returns:
        None
        """
        self.setExperimentString(DEFAULT_EXPIREMENT)

    def getExperimentNames(self):
        """returns array of the names of experiments in the JSON
            Args:
                None

            Returns:
                Array of experiments

        """
        expirementList = []
        for expirement in self._jasprExperiments['experiments']:
            expirementList.append(expirement['experimentName'])
        return expirementList

    def getExperiment(self, experimentKey):
        """returns a specific experiment dictionary

            Args:
                experimentName - the name of the experiment

            Returns:
                experiment dictionary

        """
        exp = None
        for experiment in self._jasprExperiments['experiments']:
            if experiment['experimentName'] == experimentKey:
                exp = experiment
        return exp

    def getSample(self, experimentKey, sampleKey):
        """returns a specific sample dictionary

            Args:
                experimentKey: the experiement where the sample resides
                sampleKey: the sampleKey

            Returns:
                dictionary containing sample information

        """
        exp = self.getExperiment(experimentKey)
        samp = None
        for sample in exp['dataSeries']:
            if sample['sampleName'] == sampleKey:
                samp = sample
        return samp

    def getSampleNames(self, experimentKey):
        """returns the array of sample names i

            Note:
                Do not include the `self` parameter in the ``Args`` section.

            Args:
                experimentKey: the experiment to look up

            Returns:
                True if successful, False otherwise.

        """
        samples=[]
        experiment = self.getExperiment(experimentKey)
        for sample in experiment['dataSeries']:
            samples.append(sample['sampleName'])
        return samples

    def getExperimentLabels(self, experimentKey):
        """returns the dependent and independent variable labels for
           an experiment

            Args:
                experimentKey: the experiment to look up

            Returns:
                (dependentVariableLabel as string,
                 independentVariableLabel as string)
        """
        experiment = self.getExperiment(experimentKey)
        return([experiment["dependentVariableLabel"],
                experiment["independentVariableLabel"]])

    def getSampleDataSeries(self, experimentKey, sampleKey):
        """returns the independent and dependent data series for a sample

            Args:
                experimentKey: the experiement where the sample resides
                sampleKey: the sampleKey

            Returns:
                ((dependentValues[], independentValues[])

        """
        sample = self.getSample(experimentKey,sampleKey)
        return (sample["dependentValues"],sample["independentValues"],sample["blankValue"])

#------------------------------------------------------------------------------


    def setExperimentString(self, experimentString):
        self._jasprExperiments = json.loads(experimentString)
        return None

    def getExperimentString(self):
        return json.dumps(self._jasprExperiments)
