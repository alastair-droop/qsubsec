#!/usr/bin/env python

import json
from enum import Enum

class Requirement(Enum):
    PATH_ABSENT = 'PATH_ABSENT'
    PATH_PRESENT = 'PATH_PRESENT'
    PATH_READABLE = 'PATH_READABLE'
    PATH_WRITABLE = 'PATH_WRITABLE'
    ENV_SET = 'ENV_SET'
    ENV_UNSET = 'ENV_UNSET'

class RequirementList(object):
    def __init__(self):
        super().__init__()
        self.setRequirements()
    def append(self, requirement, requirement_type):
        if not isinstance(requirement_type, Requirement):
            requirement_type = Requirement(requirement_type)
        self._requirements.append((requirement_type, requirement))
    def getRequirements(self): return self._requirements
    def setRequirements(self, requirements=[]):
        self._requirements = []
        for requirement in requirements: self.append(requirement)
    def asList(self): return [[r[0].name, r[1]] for r in self.requirements]
    def asJSON(self, indent=''): return json.dumps(self.asList(), indent=indent)
    def __getitem__(self, key): return self.requirements[key]
    def __delitem__(self, key): del(self.requirements[key])
    def __iter__(self): return iter(self.requirements)
    requirements = property(getRequirements, setRequirements, "The Requirements contained in the RequirementList")
    json = property(asJSON, None, "The Requirements list in JSON format")
