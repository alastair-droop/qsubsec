#!/usr/bin/env python3

import tokens as qstokens
import limits as qslimits
import options as qsoptions
import holds as qsholds
import requirements as qsrequirements
import logs as qslogs
import commands as qscommands
import logging as log
import json
from collections import OrderedDict

class Section(object):
    def __init__(self, name, description=None):
        super(Section, self).__init__()
        self.name = name
        self.description = description
        self.limits = qslimits.Limits()
        self.options = qsoptions.OptionList()
        self.holds = qsholds.HoldList()
        self.requirements = qsrequirements.RequirementList()
        self.outfile = qslogs.Log(qslogs.LogType.OUTPUT)
        self.errfile = qslogs.Log(qslogs.LogType.ERROR)
        self.commands = qscommands.CommandList()
    def getName(self): return self._name
    def setName(self, name): self._name = str(name)
    def getDescription(self): return self._description
    def setDescription(self, description):
        if description is None: self._description = None
        else: self._description = str(description)
    def getLimits(self): return self._limits
    def setLimits(self, limits):
        if not isinstance(limits, qslimits.Limits): raise ValueError('invalid limits type')
        self._limits = limits
    def getOptions(self): return self._options
    def setOptions(self, options):
        if not isinstance(options, qsoptions.OptionList): raise ValueError('invalid option list type')
        self._options = options
    def getHolds(self): return self._holds
    def setHolds(self, holds):
        if not isinstance(holds, qsholds.HoldList): raise ValueError('invalid hold list type')
        self._holds = holds
    def getRequirements(self): return self._requirements
    def setRequirements(self, requirements):
        if not isinstance(requirements, qsrequirements.RequirementList): raise ValueError('invalid requirement list type')
        self._requirements = requirements
    def getOutfile(self): return self._outfile
    def setOutfile(self, outfile):
        if not isinstance(outfile, qslogs.Log): raise ValueError('invalid log file type')
        self._outfile = outfile
    def getErrfile(self): return self._errfile
    def setErrfile(self, errfile):
        if not isinstance(errfile, qslogs.Log): raise ValueError('invalid log file type')
        self._errfile = errfile
    def getCommands(self): return self._commands
    def setCommands(self, commands):
        if not isinstance(commands, qscommands.CommandList): raise ValueError('invalid command list type')
        self._commands = commands
    def asDict(self):
        output = OrderedDict()
        output['name'] = self.name
        output['description'] = self.description
        output['limits'] = self.limits.limits
        output['options'] = self.options.asList()
        output['holds'] = self.holds.asList()
        output['requirements'] = self.requirements.asList()
        output['logs'] = OrderedDict()
        output['logs']['output'] = self.outfile.getFilename(self.name)
        output['logs']['error'] = self.errfile.getFilename(self.name)
        output['commands'] = self.commands.asList()
        return output
    def asJSON(self):
        return json.dumps(self.asDict())
    name = property(getName, setName, "The section ID")
    description = property(getDescription, setDescription, "The section description")
    limits = property(getLimits, setLimits, "The section limits")
    options = property(getOptions, setOptions, "The section options")
    holds = property(getHolds, setHolds, "The section hold list")
    requirements = property(getRequirements, setRequirements, "The section requirement list")
    outfile = property(getOutfile, setOutfile, "The section output log file")
    errfile = property(getErrfile, setErrfile, "The section output error file")
    commands = property(getCommands, setCommands, "The commands in the section")
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
    def __len__(self): return len(self.sections)
    def __getitem__(self, key): return self.sections[key]
    def __delitem__(self, key): del(self.sections[key])
    def __iter__(self): return iter(self.sections)
    def asJSON(self, indent=None):
        output = [s.asDict() for s in self.sections]
        return json.dumps(output, sort_keys=False, indent=indent)
    json = property(asJSON, None, "JSON representation of the section list")
    sections = property(getSections, setSections, "Return the section list")
    latest = property(getLatestSection, None, "Return the last section added")
