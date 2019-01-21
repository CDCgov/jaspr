import json
DEFAULT_CONFIG ="""{"showCurveFit":"true","blankCorrection":"false",
                     "axisScale":"LogScale",
                     "selectedAlgorithm":"logistic3"}"""

class JasprConfig(object):
    def setConfigString(self, configString):
        self._jasprConfig = json.loads(configString)
        return None

    def getConfigString(self):
        return json.dumps(self._jasprConfig)

    def getConfigSetting(self, settingKey):
        """returns a specific configuration setting

            Args:
            settingKey - settings key

            Returns:
                setting

        """
        return self._jasprConfig[settingKey]

    def loadDefaultModel(self):
        """Loads the model with UI State settings
        Returns:
        None
        """
        self.setConfigString(DEFAULT_CONFIG)

    def getConfigSettings(self):
        """returns entire settings key as a string

            Returns:
                settings string

        """
        return list(self._jasprConfig)

    def setConfigSetting(self,keyname, value):
        """sets a settings valueKey
            Args:
                keyname: key to be changed
                value: new value

            Returns:
                None
        """
        self._jasprConfig[keyname] = value
