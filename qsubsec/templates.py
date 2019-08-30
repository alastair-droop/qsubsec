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

import qsubsec.tokens as qstokens
from qsubsec.sections import Option, CommandType, Section, SectionList
from os import makedirs
from os.path import expanduser, expandvars
import logging as log
import json
from collections import OrderedDict
from urllib.request import urlopen

class Template(object):
    @classmethod
    def fromFile(cls, filename, formatter=None):
        with open(filename, 'rt') as input_file:
            input_string = input_file.read()
        return Template(string=input_string, formatter=formatter)
    @classmethod
    def fromURL(cls, url, formatter=None, encoding='UTF-8'):
        with urlopen(url) as input_url:
            input_string = input_url.read().decode(encoding)
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
    def getStringTokens(self): return self.formatter.extractTokens(self.string)
    def format(self, tokens):
        log.info('formatting template')
        if self.string is None: raise ValueError('template string unitialized')
        return tokens.resolveString(self.string)
    def execute(self, tokens):
        def QSBSection(name, description=None, check=True, log=True):
            self.sections.newSection(name, description=description, check=check, log=log)
        def QSBValidate(path):
            try: makedirs(expandvars(expanduser(path)))
            except FileExistsError: pass
            except: raise Exception('Failed to create reference log directory {}'.format(path))
        def QSBLimits(**kwargs):
            for limit, value in kwargs.items():
                self.sections.latest.limits[limit] = value
        def QSBOptions(*args):
            for option_string in args:
                self.sections.latest.options.append(Option.fromString(option_string))
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
        def QSBOutputs(path, validate=True):
            self.sections.latest.outfile.path = path
            self.sections.latest.errfile.path = path
            if validate is True: QSBValidate(path)
        def QSBCommand(cmd, name=None, test=True, log=True):
            self.sections.latest.commands.newCommand(cmd=cmd, name=name, test=test, log=log, cmdtype=CommandType.command)
        def QSBLogOutput(message):
            self.sections.latest.commands.newCommand(cmd=message, name=None, test=False, log=False, cmdtype=CommandType.log_out)            
        def QSBLogError(message):
            self.sections.latest.commands.newCommand(cmd=message, name=None, test=False, log=False, cmdtype=CommandType.log_err)
        for formatted_data in self.format(tokens):
            log.info('executing formatted template')
            exec(formatted_data, {'__sections__':self.sections, '__tokens__':tokens, 'section':QSBSection, 'validate': QSBValidate, 'limits':QSBLimits, 'options':QSBOptions, 'hold':QSBHold, 'require':QSBRequire, 'outputFile':QSBOutfile, 'errorFile':QSBErrfile, 'outputs':QSBOutputs, 'command':QSBCommand, 'message':QSBLogOutput, 'error':QSBLogError})
    formatter = property(getFormatter, setFormatter, "Formatter used for parsing tokens")
    sections = property(getSections, None, "The template sections")
    string = property(getString, setString, "The template string")
    tokens = property(getStringTokens, None, "The tokens referred to in the string")
