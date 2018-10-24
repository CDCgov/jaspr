#!/usr/bin/env python
# file sessionController.py
from flask import session
from jaspr.model import JasprModel
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
        self._initKey(CONFIG_SESSION_KEY,self.getModel().getConfigString,
                      self.getModel().setConfigString)
        self._initKey(UISTATE_SESSION_KEY,self.getModel().getUIStateString,
                      self.getModel().setUIStateString)

    def _initKey(self, keyString, getkeystringFunction,
                    setkeystringFunction):
        #if there is not a model set then load default and set session to it
        if session.get(keyString, KEY_NOT_SET) == KEY_NOT_SET:
            print("SessionController:_initKey: !!!!! No Session for: " + keyString)
            self.resetDefaultSession()
        #otherwise load the model from the session
        else:
            setkeystringFunction(session.get(keyString,'{'+keyString+': null}'))
            session.modified=True

    def getModel(self):
        return self._currentModel

    def updateUIState(self,key,value):
        self.getModel().setUIStateValue(key,value)
        session[UISTATE_SESSION_KEY] = self.getModel().getUIStateString()
        session.modified = True

    def resetDefaultSession(self):
        self.getModel().loadDefaultModel()
        session[UISTATE_SESSION_KEY] = self.getModel().getUIStateString()
        session[EXPERIMENTS_SESSION_KEY] = self.getModel().getExperimentString()
        session[CONFIG_SESSION_KEY] = self.getModel().getConfigString()
        session.modified=True
