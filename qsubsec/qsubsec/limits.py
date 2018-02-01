#!/usr/bin/env python

from collections import OrderedDict
import json

class Limits(object):
    def __init__(self):
        self.time = None
        self.vmem = None
        self.nodes = None
    def getTime(self): return self._time
    def getVMem(self): return self._vmem
    def getNodes(self): return self._nodes
    def setTime(self, time): self._time = time
    def setVMem(self, vmem): self._vmem = vmem
    def setNodes(self, nodes):
        if nodes is None: self._nodes = None
        else: self._nodes = int(nodes)
    def asDict(self):
        output = OrderedDict()
        output['time'] = self.time
        output['vmem'] = self.vmem
        output['nodes'] = self.nodes
        return output
    def asJSON(self): return json.dumps(self.asDict())
    time = property(getTime, setTime, "The specified time limit")
    vmem = property(getVMem, setVMem, "The specified vmem limit")
    nodes = property(getNodes, setNodes, "The specified node limit")
    json = property(asJSON, None, "The limits in JSON format")
