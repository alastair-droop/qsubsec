#!/usr/bin/env python

import json
from enum import Enum
import os.path

class LogType(Enum):
    OUTPUT = 'OUTPUT'
    ERROR = 'ERROR'

class Log(object):
    def __init__(self, logtype, path='.', name=None):
        self.logtype = logtype
        self.path = path
        self.name = name
    def getLogtype(self): return self._logtype
    def setLogtype(self, logtype):
        if not isinstance(logtype, LogType):
            logtype = LogType(logtype)
        self._logtype = logtype
    def getPath(self): return self._path
    def setPath(self, path): self._path = path
    def getName(self): return self._name
    def setName(self, name): self._name = name
    def getDefaultFilename(self, sectionID, taskarray=False):
        prefix_str = {'OUTPUT':'output', 'ERROR':'error'}[self.logtype.name]
        if taskarray is True: task_str = '-$TASK_ID'
        else: task_str = ''
        return '{}-{}{}.log'.format(prefix_str, sectionID, task_str)
    def getFilename(self, sectionID, taskarray=False):
        if self.name is not None: return os.path.join(self.path, self.name)
        return os.path.join(self.path, self.getDefaultFilename(sectionID, taskarray))
    logtype = property(getLogtype, setLogtype, "The log file type")
    path = property(getPath, setPath, "The log file path")
    name = property(getName, setName, "The log file name")
