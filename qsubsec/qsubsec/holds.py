#!/usr/bin/env python

import json

class HoldList(object):
    def __init__(self, holds=[]):
        self.holds = holds
    def append(self, hold):
        self._holds.append(hold)
    def getHolds(self): return self._holds
    def setHolds(self, holds=[]):
        self._holds = []
        for hold in holds: self.append(hold)
    def asList(self): return [str(h) for h in self.holds]
    def asJSON(self): return json.dumps(self.asList())
    def __getitem__(self, key): return self.holds[key]
    def __delitem__(self, key): del(self.holds[key])
    def __iter__(self): return iter(self.holds)
    holds = property(getHolds, setHolds, "The holds contained in the list")
    json = property(asJSON, None, "The holds list in JSON format")
