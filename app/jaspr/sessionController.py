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
        self._initKey(EXPERIMENTS_SESSION_KEY,self.getModel().getExperimentString)
        self._initKey(CONFIG_SESSION_KEY,self.getModel().getConfigString)
        self._initKey(UISTATE_SESSION_KEY,self.getModel().getUIStateString)

    def _initKey(self, keyString,keystringFunction):
        #if there is not a model set then load default and set session to it
        if session.get(keyString, KEY_NOT_SET) == KEY_NOT_SET:
            self.getModel().loadDefaultModel()
            session[keyString] = keystringFunction()
            session.modified=True
        #otherwise load the model from the session
        else:
            self.getModel().setExperimentString(session.get(keyString,'{'+keyString+': null}'))

    def getModel(self):
        return self._currentModel

    def updateUIState(key,value):
        session[key]=value
        self._initKey(UISTATE_SESSION_KEY,self.getModel().getUIStateString)
