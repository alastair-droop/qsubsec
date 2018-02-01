#!/usr/bin/env python

from collections import OrderedDict
import json

class Limits(object):
    def __init__(self):
        self.setLimits()
    def getLimits(self): return self._limits
    def setLimits(self, limits=OrderedDict()):
        self._limits = OrderedDict()
        for limit, value in limits:
            self.set(limit, value)
    def set(self, limit, value): self._limits[limit] = value
    def __setitem__(self, limit, value): self.set(limit, value)
    def __getitem__(self, limit): return self.limits[limit]
    def __delitem__(self, limit): del(self.limits[limit])
    def __in__(self, limit): return limit in keys(self.limits)
    def __iter__(self): return iter(self.limits)
    def asJSON(self, indent=None): return json.dumps(self.limits, indent=indent)
    limits = property(getLimits, setLimits, "The limits currently set")
    json = property(asJSON, None, "The limits in JSON representation")
