#!/usr/bin/env python

import tokens as qstokens
import options as qsoptions
from sections import Section, SectionList
import logging as log
import json
from collections import OrderedDict

class Template(object):
    @classmethod
    def fromFile(cls, filename, formatter=None):
        with open(filename, 'rt') as input_file:
            input_string = input_file.read()
        return Template(string=input_string, formatter=formatter)
    def __init__(self, string=None, formatter=None):
        self.string = string
        if formatter == None: self.formatter = qstokens.TokenFormatter()
        else: self.formatter = formatter
        self._sections = SectionList()
    def getString(self): return self._string
    def setString(self, string):
        if string is None:
            self._string = None
        else:
            self._string = str(string)
    def getFormatter(self): return self._formatter
    def setFormatter(self, formatter): self._formatter = formatter
    def getSections(self): return self._sections
    def format(self, tokens):
        if self.string is None: raise ValueError('template string unitialized')
        return tokens.resolveString(self.string)
    def execute(self, tokens):
        def QSBSection(name, description=None):
            self.sections.newSection(name, description=description)
        def QSBLimits(**kwargs):
            for limit, value in kwargs.items():
                self.sections.latest.limits[limit] = value
        def QSBOptions(*args):
            for option_string in args:
                self.sections.latest.options.append(qsoptions.Option.fromString(option_string))
        def QSBHold(*args):
            for hold_string in args:
                self.sections.latest.holds.append(hold_string)
        def QSBRequire(requirement, requirement_type):
                self.sections.latest.requirements.append(requirement, requirement_type)
        def QSBOutfile(path, name=None):
            self.sections.latest.outfile.path = path
            self.sections.latest.outfile.name = name
        def QSBErrfile(path, name=None):
            self.sections.latest.errfile.path = path
            self.sections.latest.errfile.name = name
        def QSBOutputs(path):
            self.sections.latest.outfile.path = path
            self.sections.latest.errfile.path = path
        def QSBCommand(cmd, name=None, test=True, log=True):
            self.sections.latest.commands.newCommand(cmd=cmd, name=name, test=test, log=log)
        for formatted_data in self.format(tokens):
            exec(formatted_data, {'__sections__':self.sections, 'section':QSBSection, 'limits':QSBLimits, 'options':QSBOptions, 'hold':QSBHold, 'require':QSBRequire, 'outputFile':QSBOutfile, 'errorFile':QSBErrfile, 'outputs':QSBOutputs, 'command':QSBCommand})
    formatter = property(getFormatter, setFormatter, "Formatter used for parsing tokens")
    sections = property(getSections, None, "The template sections")
    string = property(getString, setString, "The template string")
