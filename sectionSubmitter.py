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
import subprocess

class outputSubmitterBase(object):
    pass

class outputSubmitterProc(outputSubmitterBase):
    @classmethod
    def spawn(cls, proc_exec, data, timeout=None):
        # Attempt to create the subprocess:
        log.info('spawning process "{}" using process submitter'.format(' '.join(proc_exec)))
        try:
            proc = subprocess.Popen(args=proc_exec, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
            log.debug('spawned subprocess pid {}'.format(proc.pid))
        except FileNotFoundError as err:
            log.error(log, 'subprocess executable "{}" not found'.format(args[0]))
            raise err
        except Exception as err:
            log.error(log, 'failed to spawn subprocess "{}"'.format(' '.join(proc_exec)))
            raise err
        # Attempt to communicate with the subprocess:
        try:
            log.debug('sending {} bytes to subprocess {}'.format(len(data), proc.pid))
            output_data = proc.communicate(input=data, timeout=timeout)
            if (output_data[0] != None) and (output_data[0] != ''): log.info('submission stdout: "{}"'.format(output_data[0].strip()))
            if (output_data[1] != None) and (output_data[1] != ''): log.info('submission stderr: "{}"'.format(output_data[1].strip()))
        except subprocess.TimeoutExpired as err:
            proc.kill()
            proc.communicate()
            log.warning('submission to subprocess "{}" timed out'.format(' '.join(proc_exec)))
            raise err
        except Exception as err:
            proc.kill()
            proc.communicate()
            log.warning('failed to submit job to subprocess "{}"'.format(' '.join(proc_exec)))
            raise err

class outputSubmitterShell(outputSubmitterBase):
    @classmethod
    def spawn(cls, proc_exec, data, timeout=None):
        proc_exec = ' '.join(proc_exec)
        # Attempt to create the subprocess:
        log.info('spawning process using "{}" shell ({} bytes)'.format(proc_exec, len(data)))
        try:
            pid = subprocess.Popen(args=data, executable=proc_exec, stdin=None, stdout=None, shell=True).pid
            log.debug('spawned "{}" shell pid {}'.format(proc_exec, pid))
        except Exception as err:
            log.error(log, 'failed to run command in "{}" shell'.format(proc_exec))
            raise err
