#!/usr/bin/env python
# file sessionController.py
from flask import session
from Model import JasprModel

"""
This module manages the transfer of state to and from the session

Todo:
    * None at this time
"""

class SessionController(object):

    def __init__(self, currentSession, currentModel):
        self._currentSession = currentSession
        self._currentModel = currentModel

    def loadModel(self):
        #todo implement
        return self._currentModel

    def saveModel(self):
        #todo implement
        return True
