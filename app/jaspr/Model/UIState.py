#!/usr/bin/env python
# file UIState.py
import json

DEFAULT_UISTATE="""{"currentExperiment":"Anscombe", "currentSample":"Set I"}"""

class UIState(object):
    """
    This is the model to handle the UI State of the application per session
    The information stored is as follows:
    {
        "currentExperiment":"experiment name",
        "currentSample":"sample name"
    }
    """
    def __init__(self):
        """ initialize with config and experiment data
        Args:
        jasprConfig: JSON string of config information
        jasprExperiment: JSON string of expriemen
        """
        self._currentExperiment=""
        self._currentSample=""

    def loadDefaultModel(self):
        """Loads the model with UI State settings
        Returns:
        None
        """
        self.setUIStateString(DEFAULT_UISTATE)

    def setUIStateValue(self, keyname, value):
        """sets a ui valueKey
            Args:
                keyname: key to be changed
                value: new value

            Returns:
                None
        """
        self._jasprUIState[keyname] = value

    def getUIStateValue(self, statekey):
        """returns a specific configuration setting

            Args:
            settingKey - settings key

            Returns:
                setting

        """
        return self._jasprUIState[statekey]

    def setUIStateString(self, uiStateString):
            self._jasprUIState = json.loads(uiStateString)
            return None

    def getUIStateString(self):
        return json.dumps(self._jasprUIState)
