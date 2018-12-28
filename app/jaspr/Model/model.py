#!/usr/bin/env python
# file model.py
from jaspr.Model.UIState import UIState
from jaspr.Model.jasprConfig import JasprConfig
from jaspr.Model.experiments import Experiments

class JasprModel(object):
    """
    This is the Model class for the application.
    The information stored is as follows:
    _jasprUIState: a class containing the UI state for this session
    _jasprConfig: a class containing the configuration status for this session
    _jasprExperiments: a class containing the experiment data

    """
    def __init__(self):
        """ initialize with empty data
        """
        self._jasprExperiments = Experiments();
        self._jasprConfig = JasprConfig();
        self._uiState = UIState();

    def loadDefaultModel(self):
        """Loads the model with hardcoded sample session data (anscombs quartet)
        and default config settings
        Returns:
        None
        """
        self._jasprExperiments.loadDefaultModel()
        self._jasprConfig.loadDefaultModel()
        self._uiState.loadDefaultModel()
