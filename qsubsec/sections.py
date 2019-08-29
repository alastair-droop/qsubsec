# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging as log
import json
from enum import Enum
from collections import OrderedDict
import re
import os

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
    def asDict(self):
        output = OrderedDict()
        output['logtype'] = self.logtype.name
        output['path'] = self.path
        output['name'] = self.name
        return output
    logtype = property(getLogtype, setLogtype, "The log file type")
    path = property(getPath, setPath, "The log file path")
    name = property(getName, setName, "The log file name")

class Option(object):
    @classmethod
    def fromString(cls, string):
        if string.startswith('-'):
            string = string.lstrip('-')
        return Option(string)
    def __init__(self, string):
        self.value = string
    def setValue(self, value): self._value = value
    def getValue(self): return self._value
    def __str__(self, prefix='-'): return '{}{}'.format(prefix, self.value)
    value = property(getValue, setValue)

class OptionList(object):
    def __init__(self):
        super().__init__()
        self.setOptions()
    def append(self, option):
        if not isinstance(option, Option): raise ValueError('invalid option type')
        self._options.append(option)
    def getOptions(self): return self._options
    def setOptions(self, options=[]):
        self._options = []
        for option in options: self.append(option)
    def asList(self): return [str(o) for o in self.options]
    def asJSON(self): return json.dumps(self.asList())
    def __getitem__(self, key): return self.options[key]
    def __delitem__(self, key): del(self.options[key])
    def __iter__(self): return iter(self.options)
    options = property(getOptions, setOptions, "The Options contained in the OptionList")
    json = property(asJSON, None, "The Options list in JSON format")

class Requirement(Enum):
    PATH_ABSENT = 'PATH_ABSENT'
    PATH_PRESENT = 'PATH_PRESENT'
    PATH_READABLE = 'PATH_READABLE'
    PATH_WRITABLE = 'PATH_WRITABLE'
    PATH_EXECUTABLE = 'PATH_EXECUTABLE'
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

class CommandType(Enum):
    command = 'command'
    log_out = 'log_out'
    log_err = 'log_err'

class Command(object):
    def __init__(self, cmd, name=None, log=True, test=True, cmdtype=CommandType.command):
        self.cmdtype = cmdtype
        self.command = cmd
        self.name = name
        self.log = log
        self.test = test
        self.include = True
    def getType(self): return self._cmdtype
    def setType(self, cmdtype): self._cmdtype = cmdtype
    def getCommand(self): return self._command
    def setCommand(self, cmd): self._command = str(cmd)
    def getLog(self): return self._log
    def setLog(self, log): self._log = bool(log)
    def getTest(self): return self._test
    def setTest(self, test): self._test = bool(test)
    def getName(self): return self._name
    def setName(self, name): self._name = name
    def getInclude(self): return self._include
    def setInclude(self, include): self._include = bool(include)
    def asDict(self):
        output = OrderedDict()
        output['type'] = self.cmdtype.name
        output['name'] = self.name
        output['command'] = self.command
        output['log'] = self.log
        output['test'] = self.test
        return output
    def asJSON(delf, indent=None): return json.dumps(self.asDict, indent=indent)
    command = property(getCommand, setCommand, doc='The QSUB command string')
    cmdtype = property(getType, setType, doc='The command type')
    log = property(getLog, setLog, doc='Should the command log its status?')
    test = property(getTest, setTest, doc='Should the command test for completion?')
    name = property(getName, setName, doc='The QSUB command Name')
    include = property(getInclude, setInclude, doc='Include command in output?')
    json = property(asJSON, None, "The command in JSON format")

class CommandList(object):
    def __init__(self):
        self.commands = []
    def getCommands(self): return self._commands
    def setCommands(self, commands):
        self._commands = []
        for command in commands:
            self.append(command)
    def getNames(self):
        output = []
        for command in self._commands:
            output.append(command.name)
        return output
    def append(self, new):
        if not isinstance(new, Command): raise TypeError('invalid command type')
        self._commands.append(new)
    def newCommand(self, cmd, name=None, test=True, log=True, cmdtype=CommandType.command):
        cmd_n = 0
        for i in self.commands:
            if i.cmdtype == CommandType.command: cmd_n += 1
        if name == None: name = '{0}'.format(hex(cmd_n + 1))
        self.append(Command(cmd=cmd, name=name, test=test, log=log, cmdtype=cmdtype))
    def asList(self): return [c.asDict() for c in self.commands]
    def asJSON(self, indent=None): return json.dumps(self.asList(), indent=indent)
    def __len__(self): return len(self.commands)
    def __getitem__(self, key): return self.commands[key]
    def __delitem__(self, key): del(self.commands[key])
    def __iter__(self): return iter(self.commands)
    commands = property(getCommands, setCommands, "The commands in the list")
    names = property(getNames, None, "The command names in the list")
    json = property(asJSON, None, "The command list in JSON format")

class Section(object):
    def __init__(self, name, description=None, check=True, log=True):
        super(Section, self).__init__()
        self.name = name
        self.description = description
        self.check = check
        self.log = log
        self.limits = Limits()
        self.options = OptionList()
        self.holds = HoldList()
        self.requirements = RequirementList()
        self.outfile = Log(LogType.OUTPUT)
        self.errfile = Log(LogType.ERROR)
        self.commands = CommandList()
    def getName(self): return self._name
    def setName(self, name): self._name = str(name)
    def getDescription(self): return self._description
    def setDescription(self, description):
        if description is None: self._description = None
        else: self._description = str(description)
    def getCheck(self): return self._check
    def setCheck(self, check): self._check = bool(check)
    def getLog(self): return self._log
    def setLog(self, log): self._log = bool(log)
    def getLimits(self): return self._limits
    def setLimits(self, limits):
        if not isinstance(limits, Limits): raise ValueError('invalid limits type')
        self._limits = limits
    def getOptions(self): return self._options
    def setOptions(self, options):
        if not isinstance(options, OptionList): raise ValueError('invalid option list type')
        self._options = options
    def getHolds(self): return self._holds
    def setHolds(self, holds):
        if not isinstance(holds, HoldList): raise ValueError('invalid hold list type')
        self._holds = holds
    def getRequirements(self): return self._requirements
    def setRequirements(self, requirements):
        if not isinstance(requirements, RequirementList): raise ValueError('invalid requirement list type')
        self._requirements = requirements
    def getOutfile(self): return self._outfile
    def setOutfile(self, outfile):
        if not isinstance(outfile, Log): raise ValueError('invalid log file type')
        self._outfile = outfile
    def getErrfile(self): return self._errfile
    def setErrfile(self, errfile):
        if not isinstance(errfile, Log): raise ValueError('invalid log file type')
        self._errfile = errfile
    def getCommands(self): return self._commands
    def setCommands(self, commands):
        if not isinstance(commands, CommandList): raise ValueError('invalid command list type')
        self._commands = commands
    def asDict(self):
        output = OrderedDict()
        output['name'] = self.name
        output['description'] = self.description
        output['check'] = self.check
        output['log'] = self.log
        output['limits'] = self.limits.limits
        output['options'] = self.options.asList()
        output['holds'] = self.holds.asList()
        output['requirements'] = self.requirements.asList()
        output['logs'] = OrderedDict()
        output['logs']['output'] = self.outfile.asDict()
        output['logs']['error'] = self.errfile.asDict()
        output['commands'] = self.commands.asList()
        return output
    def asJSON(self):
        return json.dumps(self.asDict())
    name = property(getName, setName, "The section ID")
    description = property(getDescription, setDescription, "The section description")
    check = property(getCheck, setCheck, "The section check flag")
    log = property(getLog, setLog, "The section logging flag")
    limits = property(getLimits, setLimits, "The section limits")
    options = property(getOptions, setOptions, "The section options")
    holds = property(getHolds, setHolds, "The section hold list")
    requirements = property(getRequirements, setRequirements, "The section requirement list")
    outfile = property(getOutfile, setOutfile, "The section output log file")
    errfile = property(getErrfile, setErrfile, "The section output error file")
    commands = property(getCommands, setCommands, "The commands in the section")
    json = property(asJSON, None, "The section in JSON representation")

class SectionList(object):
    @classmethod
    def fromJSONFile(cls, json_file):
        with open(json_file, 'rt') as handle:
            input_json = json.load(handle)
        output = SectionList()
        for s in input_json:
            new_section = Section(name=s['name'], description=s['description'], check=s['check'], log=s['log'])
            for l in s['limits'].keys(): new_section.limits[l] = s['limits'][l]
            for o in s['options']: new_section.options.append(Option.fromString(o))
            for h in s['holds']: new_section.holds.append(h)
            for r in s['requirements']: new_section.requirements.append(r[1], r[0])
            new_section.outfile.logtype = s['logs']['output']['logtype']
            new_section.outfile.path = s['logs']['output']['path']
            new_section.outfile.name = s['logs']['output']['name']
            new_section.errfile.logtype = s['logs']['error']['logtype']
            new_section.errfile.path = s['logs']['error']['path']
            new_section.errfile.name = s['logs']['error']['name']
            for c in s['commands']: new_section.commands.newCommand(c['command'], name=c['name'], test=c['test'], log=c['log'], cmdtype=CommandType(c['type']))
            output.append(new_section)
        return output
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
    def newSection(self, name, description=None, check=True, log=True):
        new = Section(name=name, description=description, check=check, log=log)
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
