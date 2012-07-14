#===============================================================================
# Copyright 2011 Jake Ross
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================



#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from src.scripts.core.core_script_parser import CoreScriptParser


class BakeoutScriptParser(CoreScriptParser):
    COMMAND_KEYS = ['CONFIG', 'GOTO', 'MAINTAIN', 'RAMP']

    def raw_parse(self, args):
        error = None
        sargs = 'Setpoint(C), Duration(min)'
#        print args
        if len(args) < 2 or (len(args) == 2 and not args[1]):
            error = 'Not enough args ' + sargs
        elif len(args) > 2:
            error = 'Too many args ' + sargs
        else:
            #check all are numbers

            error = self._check_number(args)

        return error, args

    def _ramp_parse(self, linenum, **kw):
#        print 'adasd'
#        print '----------------'
        err = 'Not enough args'

        tok = self.get_token()
        toks = tok.split(',')
        nargs = len(toks)

        #tdict = {'m':'m', 's':'s', 'h':'h' }

#        check_time_units = lambda x: tdict[x]
#        arg_map = [float, float, float, check_time_units, int]
        arg_map = [float, float, float, float]#, check_time_units, int]
        args = None
#        if not toks[-1] == '' and nargs <= 5 and nargs >= 2:
        if not toks[-1] == '' and 2 <= nargs <= 4:
            args = []
            for ti, am in zip(toks, arg_map):
                try:
                    args.append(am(ti))
                except (ValueError, AttributeError), e:
                    if not ti in ['', None]:
                        err = str(e)
                    break
#                except KeyError:
#                    err = 'Invalid time unit {}'.format(ti)
#                    break
            else:
                err = None

        elif nargs > 4:
            err = 'Too many arguments'

        return err, args

    def _goto_parse(self, linenum, **kw):

        return self._get_float()

    def _maintain_parse(self, linenum, **kw):
        return self._get_float()
#============= EOF ====================================
