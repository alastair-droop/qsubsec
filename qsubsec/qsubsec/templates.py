#!/usr/bin/env python

import tokens as qstokens
from sections import Section, SectionList
import logging as log
import json
from collections import OrderedDict

class Template(object):
    def __init__(self, string, formatter=None):
        self.string = string
        if formatter == None: self.formatter = qstokens.TokenFormatter()
        else: self.formatter = formatter
        self._sections = SectionList()
    def getString(self): return self._string
    def setString(self, string): self._string = str(string)
    def getFormatter(self): return self._formatter
    def setFormatter(self, formatter): self._formatter = formatter
    def getSections(self): return self._sections
    def format(self, tokens):
        return tokens.resolveString(self.string)
    def execute(self, tokens):
        def QSBSection(name, description=None):
            self.sections.newSection(name, description=description)
        
        for formatted_data in self.format(tokens):
            exec(formatted_data, {'section':QSBSection})
    formatter = property(getFormatter, setFormatter, "Formatter used for parsing tokens")
    sections = property(getSections, None, "The template sections")
    string = property(getString, setString, "The template string")

ts = qstokens.TFFParser().parse('test.tff')
t = Template('section("TEST_{NAME}")')
# t = Template('print("Hello, {NAME}.")')
t.execute(ts)

print(t.sections.asJSON(indent='\t'))

