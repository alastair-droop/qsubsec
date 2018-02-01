#!/usr/bin/env python3

import tokens as qstokens
import logging as log
import json
from collections import OrderedDict

class Section(object):
    def __init__(self, name, description=None):
        super(Section, self).__init__()
        self.name = name
        self.description = description
    def getName(self): return self._name
    def setName(self, name): self._name = str(name)
    def getDescription(self): return self._description
    def setDescription(self, description):
        if description is None: self._description = None
        else: self._description = str(description)
    def asDict(self):
        output = OrderedDict()
        output['name'] = self.name
        output['description'] = self.description
        return output
    def asJSON(self):
        return json.dumps(self.asDict())
    name = property(getName, setName, "The section ID")
    description = property(getDescription, setDescription, "The section description")
    json = property(asJSON, None, "The section in JSON representation")

class SectionList(object):
    def __init__(self):
        self.sections = []
    def append(self, section):
        if not isinstance(section, Section): raise ValueError('invalid section type')
        self._sections.append(section)
    def getSections(self): return self._sections
    def getLatestSection(self): return self._sections[-1]
    def setSections(self, sections=[]):
        self._sections = []
        for sections in sections: self.append(section)
    def newSection(self, name, description=None):
        new = Section(name=name, description=description)
        self.append(new)
    def __getitem__(self, key): return self.sections[key]
    def __delitem__(self, key): del(self.sections[key])
    def __iter__(self): return iter(self.sections)
    def asJSON(self, indent=None):
        output = [s.asDict() for s in self.sections]
        return json.dumps(output, sort_keys=False, indent=indent)
    json = property(asJSON, None, "JSON representation of the section list")
    sections = property(getSections, setSections, "Return the section list")
    latest = property(getLatestSection, None, "Return the last section added")
