#!/usr/bin/env python
# file sessionController.py
from flask import session
from jaspr.Model.model import JasprModel
import json

EXPERIMENTS_SESSION_KEY = "experiments"
CONFIG_SESSION_KEY = "config"
UISTATE_SESSION_KEY = "uistate"
KEY_NOT_SET = "NOT SET"
"""
This module manages the transfer of state to and from the session

Todo:
    * None at this time
"""

class SessionController(object):

    def __init__(self):
        self._currentModel = JasprModel()
        self._initKey(EXPERIMENTS_SESSION_KEY,self.getModel().getExperimentString,
                      self.getModel().setExperimentString)
        self._initKey(CONFIG_SESSION_KEY,self.getModel()._jasprConfig.getConfigString,
                      self.getModel()._jasprConfig.setConfigString)
        self._initKey(UISTATE_SESSION_KEY,self.getModel()._uiState.getUIStateString,
                      self.getModel()._uiState.setUIStateString)

    def _initKey(self, keyString, getkeystringFunction,
                    setkeystringFunction):
        #if there is not a model set then load default and set session to it
        if session.get(keyString, KEY_NOT_SET) == KEY_NOT_SET:
            print("***************************************************")
            print("SessionController:_initKey couldn't find: {} in {}".format(keyString, session))
            self.resetDefaultSession()
            print("***************************************************")
        #otherwise load the model from the session
        else:
            setkeystringFunction(session.get(keyString,'{'+keyString+': null}'))
            session.modified=True

    def getModel(self):
        return self._currentModel

    def updateUIState(self,key,value):
        self.getModel()._uiState.setUIStateValue(key,value)
        session[UISTATE_SESSION_KEY] = self.getModel()._uiState.getUIStateString()
        session.modified = True

    def resetDefaultSession(self):
        print("SessionController:resetDefaultSession: Session being cleared")
        session.clear()
        self.getModel().loadDefaultModel()
        self.loadSessionFromModel()

    def resetUISession(self):
        experimentKey = self.getModel().getExperimentNames()[0]
        self.updateUIState("currentExperiment", experimentKey)
        self.updateUIState("currentSample", self.getModel().\
                getSampleNames(experimentKey)[0])

    def loadSessionFromModel(self):
        session[UISTATE_SESSION_KEY] = self.getModel()._uiState.getUIStateString()
        session[EXPERIMENTS_SESSION_KEY] = self.getModel().getExperimentString()
        session[CONFIG_SESSION_KEY] = self.getModel()._jasprConfig.getConfigString()
        session.modified=True
