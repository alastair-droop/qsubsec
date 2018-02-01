#!/usr/bin/env python

from collections import OrderedDict
import json

class Command(object):
    def __init__(self, cmd, name=None, log=True, test=True):
        self.command = cmd
        self.name = name
        self.log = log
        self.test = test
    def getCommand(self): return self._command
    def setCommand(self, cmd): self._command = str(cmd)
    def getLog(self): return self._log
    def setLog(self, log): self._log = bool(log)
    def getTest(self): return self._test
    def setTest(self, test): self._test = bool(test)
    def getName(self): return self._name
    def setName(self, name): self._name = name
    def asDict(self):
        output = OrderedDict()
        output['name'] = self.name
        output['command'] = self.command
        output['log'] = self.log
        output['test'] = self.test
        return output
    def asJSON(delf, indent=None): return json.dumps(self.asDict, indent=indent)
    command = property(getCommand, setCommand, doc='The QSUB command string')
    log = property(getLog, setLog, doc='Should the command log its status?')
    test = property(getTest, setTest, doc='Should the command test for completion?')
    name = property(getName, setName, doc='The QSUB command Name')
    json = property(asJSON, None, "The command in JSON format")

class CommandList(object):
    def __init__(self):
        self.commands = []
    def getCommands(self): return self._commands
    def setCommands(self, commands):
        self._commands = []
        for command in commands:
            self.append(command)
    def append(self, new):
        if not isinstance(new, Command): raise TypeError('invalid command type')
        self._commands.append(new)
    def newCommand(self, cmd, name=None, test=True, log=True):
        if name == None: name = '{0}'.format(hex(len(self.commands) + 1))
        self.append(Command(cmd=cmd, name=name, test=test, log=log))
    def asList(self): return [c.asDict() for c in self.commands]
    def asJSON(self, indent=None): return json.dumps(self.asList(), indent=indent)
    def __len__(self): return len(self.commands)
    def __getitem__(self, key): return self.commands[key]
    def __delitem__(self, key): del(self.commands[key])
    def __iter__(self): return iter(self.commands)
    commands = property(getCommands, setCommands, "The commands in the list")
    json = property(asJSON, None, "The command list in JSON format")
    

    # def __init__(self):
    #     self.sections = []
    # def append(self, section):
    #     if not isinstance(section, Section): raise ValueError('invalid section type')
    #     self._sections.append(section)
    # def getSections(self): return self._sections
    # def getLatestSection(self): return self._sections[-1]
    # def setSections(self, sections=[]):
    #     self._sections = []
    #     for sections in sections: self.append(section)
    # def newSection(self, name, description=None):
    #     new = Section(name=name, description=description)
    #     self.append(new)
    # def __len__(self): return len(self.sections)
    # def __getitem__(self, key): return self.sections[key]
    # def __delitem__(self, key): del(self.sections[key])
    # def __iter__(self): return iter(self.sections)
    # def asJSON(self, indent=None):
    #     output = [s.asDict() for s in self.sections]
    #     return json.dumps(output, sort_keys=False, indent=indent)
    # json = property(asJSON, None, "JSON representation of the section list")
    # sections = property(getSections, setSections, "Return the section list")
    # latest = property(getLatestSection, None, "Return the last section added")
