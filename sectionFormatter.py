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

from sections import Requirement, CommandType
from os import remove
from collections import OrderedDict
import logging as log
import json

class OutputFormatter(object):
    option_prefix = '#'
    newline = '\n'
    @classmethod
    def timestampString(cls): return '`date`'
    @classmethod
    def echoString(cls, message, timestamp=True):
        if timestamp is True: prefix = '[{}]: '.format(cls.timestampString())
        else: prefix = ''
        return 'echo "{}{}"'.format(prefix, message)
    @classmethod
    def frontMatter(cls, section):
        return []
    @classmethod
    def commands(cls, section):
        return []
    @classmethod
    def endMatter(cls, section):
        return []
    @classmethod
    def format(cls, section):
        output = []
        output.extend(cls.frontMatter(section))
        output.extend(cls.commands(section))
        output.extend(cls.endMatter(section))
        return output

class BashFormatter(OutputFormatter):
    @classmethod
    def frontMatter(cls, section):
        output = []
        for requirement, name in section.requirements:
            if requirement == Requirement.PATH_ABSENT: output.append('if ! test -e {0}; then {1}; exit 1; fi'.format(name, cls.echoString('ERROR: file {} exists'.format(name))))
            if requirement == Requirement.PATH_PRESENT: output.append('if test -e {0}; then {1}; exit 1; fi'.format(name, cls.echoString('ERROR: file {} not found'.format(name))))
            if requirement == Requirement.PATH_READABLE: output.append('if ! test -r {0}; then {1} >> {2}; exit 1; fi'.format(name, cls.echoString('ERROR: file {} not readable'.format(name)), section.errfile.getFilename(section.name)))
            if requirement == Requirement.PATH_WRITABLE: output.append('if ! test -w {0}; then {1} >> {2}; exit 1; fi'.format(name, cls.echoString('ERROR: file {} not writable'.format(name)), section.errfile.getFilename(section.name)))
            if requirement == Requirement.PATH_EXECUTABLE: output.append('if [ ! -x "$(command -v {0})" ]; then {1} >> {2}; exit 1; fi'.format(name, cls.echoString('ERROR: file {} not executable'.format(name)), section.errfile.getFilename(section.name)))
            if requirement == Requirement.ENV_SET: output.append('if [ -z ${{{0}+x}} ]; then {1} >> {2}; exit 1; fi'.format(name, cls.echoString('ERROR: environment variable {} not set'.format(name)), section.errfile.getFilename(section.name)))
            if requirement == Requirement.ENV_UNSET: output.append('if [ -n ${{{0}+x}} ]; then {1} >> {2}; exit 1; fi'.format(name, cls.echoString('ERROR: environment variable {} set'.format(name)), section.errfile.getFilename(section.name)))
        if section.log is True: output.append('{0} >> {1}'.format(cls.echoString('section {} started'.format(section.name)), section.outfile.getFilename(section.name)))
        return output
    @classmethod
    def commands(cls, section):
        output = []
        for command in section.commands:
            if command.cmdtype is CommandType.log_out:
                output.append('{0} >> {1}'.format(cls.echoString('{}'.format(command.command)), section.outfile.getFilename(section.name)))
            elif command.cmdtype is CommandType.log_err:
                output.append('{0} >> {1}'.format(cls.echoString('{}'.format(command.command)), section.errfile.getFilename(section.name)))
            else:            
                if command.log is True: output.append('{0} >> {1}'.format(cls.echoString('command {} started'.format(command.name)), section.outfile.getFilename(section.name)))
                if command.test is True: output.append('{0} || {{ {1} >> {2}; exit 1; }}'.format(command.command, cls.echoString('command {} failed'.format(command.name)), section.errfile.getFilename(section.name)))
                else: output.append(command.command)
                if command.log is True: output.append('{0} >> {1}'.format(cls.echoString('command {} completed'.format(command.name)), section.outfile.getFilename(section.name)))
        return output
    @classmethod
    def endMatter(cls, section):
        output = []
        if section.log is True: output.append('{0} >> {1}'.format(cls.echoString('section {} completed'.format(section.name)), section.outfile.getFilename(section.name)))
        return output

class QSUBFormatter(OutputFormatter):
    option_prefix = '#$'
    @classmethod
    def frontMatter(cls, section):
        output = []
        output.append('{} -N {}'.format(cls.option_prefix, section.name))
        for limit, value in section.limits.limits.items():
            output.append('{} -l {}={}'.format(cls.option_prefix, limit, value))
        for option in section.options:
            output.append('{} {}'.format(cls.option_prefix, str(option)))
        for hold in section.holds:
            output.append('{} -hold_jid {}'.format(cls.option_prefix, hold))
        output.append('{} -o {}'.format(cls.option_prefix, section.outfile.getFilename(section.name)))
        output.append('{} -e {}'.format(cls.option_prefix, section.errfile.getFilename(section.name)))
        for requirement, name in section.requirements:
            if requirement == Requirement.PATH_ABSENT: output.append('if ! test -e {0}; then {1}; exit 1; fi'.format(name, cls.echoString('ERROR: file {} exists'.format(name))))
            if requirement == Requirement.PATH_PRESENT: output.append('if test -e {0}; then {1}; exit 1; fi'.format(name, cls.echoString('ERROR: file {} not found'.format(name))))
            if requirement == Requirement.PATH_READABLE: output.append('if ! test -r {0}; then {1}; exit 1; fi'.format(name, cls.echoString('ERROR: file {} not readable'.format(name))))
            if requirement == Requirement.PATH_WRITABLE: output.append('if ! test -w {0}; then {1}; exit 1; fi'.format(name, cls.echoString('ERROR: file {} not writable'.format(name))))
            if requirement == Requirement.PATH_EXECUTABLE: output.append('if [ ! -x "$(command -v {0})" ]; then {1} >> {2}; exit 1; fi'.format(name, cls.echoString('ERROR: file {} not executable'.format(name)), section.errfile.getFilename(section.name)))
            if requirement == Requirement.ENV_SET: output.append('if [ -z ${{{0}+x}} ]; then {1}; exit 1; fi'.format(name, cls.echoString('ERROR: environment variable {} not set'.format(name))))
            if requirement == Requirement.ENV_UNSET: output.append('if [ -n ${{{0}+x}} ]; then {1}; exit 1; fi'.format(name, cls.echoString('ERROR: environment variable {} set'.format(name))))
        if section.check is True:
            output.append('on_stop() {{ {}; }}'.format(cls.echoString('imminent SIGSTOP (received SIGUSR1)')))
            output.append('on_kill() {{ {}; }}'.format(cls.echoString('imminent SIGKILL (received SIGUSR2)')))
            output.append('trap \'on_stop\' SIGUSR1')
            output.append('trap \'on_kill\' SIGUSR2')
        if section.log is True: output.append(cls.echoString('section {} started'.format(section.name)))
        return output
    @classmethod
    def commands(cls, section):
        output = []
        for command in section.commands:
            if command.cmdtype is CommandType.log_out:
                output.append('{0} >> {1}'.format(cls.echoString('{}'.format(command.command)), section.outfile.getFilename(section.name)))
            elif command.cmdtype is CommandType.log_err:
                output.append('{0} >> {1}'.format(cls.echoString('{}'.format(command.command)), section.errfile.getFilename(section.name)))
            else:
                if command.log is True: output.append(cls.echoString('command {} started'.format(command.name)))
                if command.test is True: output.append('{0} || {{ {1}; exit 1; }}'.format(command.command, cls.echoString('command {} failed'.format(command.name))))
                else: output.append(command.command)
                if command.log is True: output.append(cls.echoString('command {} completed'.format(command.name)))
        return output
    @classmethod
    def endMatter(cls, section):
        output = []
        if section.log is True: output.append(cls.echoString('section {} completed'.format(section.name)))
        return output
