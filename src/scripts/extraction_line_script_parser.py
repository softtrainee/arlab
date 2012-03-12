'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
#from traits.api import HasTraits, on_trait_change, Str, Int, Float, Button
#from traitsui.api import View, Item, Group, HGroup, VGroup

#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.scripts.core.core_script_parser import CoreScriptParser
from src.helpers.filetools import str_to_bool
from src.helpers import paths
VALID_ACTIONS = ['OPEN', 'CLOSE', 'Open', 'Close', 'open', 'close']

RUNSCRIPT_DIR = os.path.join(paths.scripts_dir, 'runscripts')
class ExtractionLineScriptParser(CoreScriptParser):
    COMMAND_KEYS = ['LOG', 'VALVE', 'WAIT', 'SUB', 'IF', 'WARNING', 'DEVICE', 'MEASURE', 'MOVE_TO_HOLE',
                'ENABLE_LASER', 'DISABLE_LASER', 'SET_LASER_POWER', 'CLOSE_STAGE_MANAGER',
                'SET_BEAM_DIAMETER', 'SET_TIME_ZERO', 'CONFIG', 'DEFINE', 'SNIFF', 'EXTRACTION_ANALYSIS'
                ]

    def _get_subroutine_path_(self, subroutine):
        '''
            @type subroutine: C{str}
            @param subroutine:
        '''
        if '.' in subroutine:
            sub = RUNSCRIPT_DIR
            for b in subroutine.split('.'):
                sub = os.path.join(sub, b)
            subroutine = sub
        return os.path.join(RUNSCRIPT_DIR, '%s.rs' % subroutine)

    def _check_valid_subroutine_(self, subroutine):
        '''
        '''
        path = self._get_subroutine_path_(subroutine.strip())

        if path and os.path.isfile(path):
            return path

    def _sniff_parse(self, linenum, **kw):
        error = None
        lexer = self._lexer
        sniffname = lexer.get_token()
        if sniffname is None:
            error = 'Expected a sniff configuration name'
        else:
            error = self._check_extra_args(lexer)

        sniffdir = os.path.join(RUNSCRIPT_DIR, 'sniff')
        kw['sniffpath'] = os.path.join(sniffdir, sniffname)

        return error, None
    def _extraction_analysis_parse(self, linenum, **kw):
        error = None
        lexer = self._lexer
        eaname = lexer.get_token()
        if eaname is None:
            error = 'Expected a EA configuration name'
        else:
            error = self._check_extra_args(lexer)

        eadir = os.path.join(RUNSCRIPT_DIR, 'extraction_analysis')
        kw['extraction_analysis_path'] = os.path.join(eadir, eaname)

        return error, None

    def _define_parse(self, linenum, **kw):
        error = None
        lexer = self._lexer
        kw = dict()
        token = lexer.get_token().strip()
        if '=' not in token:
            error = 'Expected key = value'
        elif token.endswith('='):
            error = 'Expected key = value'
        else:
            key, value = token.split('=')
            bval = str_to_bool(value)
            if bval is not None:
                value = bval
            else:
                try:
                    value = float(value)
                except ValueError:
                    pass
            kw[key] = value

        return error, kw

    def _measure_parse(self, linenum, **kw):
        '''

        '''
        lexer = self._lexer
        error = self._check_extra_args(lexer)

        return error, None

    def _warning_parse(self, linenum, **kw):
        '''

        '''
        return self._log_parse(linenum)

#    def _set_time_zero_parse(self, linenum, **kw):
#        lexer = self._lexer
#        error, args, kw = self._get_arguments(lexer)
#        if error is None:
#            error = self._check_extra_args(lexer)
#        return error,

    def _move_to_hole_parse(self, linenum, **kw):
        lexer = self._lexer
        error, args, kw = self._get_arguments(lexer)
        hole = None
        if error is None:
            try:
                if '%' not in args[0]:
                    hole = int(args[0])
                else:
                    hole = args[0]
            except ValueError:
                error = 'Invalid hole argument %s ' % args[0]
            except TypeError:
                error = 'Expected a int or mapping key'

        if error is None:
            error = self._check_extra_args(lexer)

        return error, hole, kw


    def _close_stage_manager_parse(self, linenum, **kw):
        lexer = self._lexer
        error = self._check_extra_args(lexer)
        return error,

    def _enable_laser_parse(self, linenum, **kw):
        lexer = self._lexer
        error = self._check_extra_args(lexer)
        return error,

    def _disable_laser_parse(self, linenum, **kw):
        lexer = self._lexer
        error = self._check_extra_args(lexer)
        return error,

    def _set_beam_diameter_parse(self, linenum, **kw):
        lexer = self._lexer
        error, args, kw = self._get_arguments(lexer)
        diameter = None
        if error is None:
            try:
                if '%' not in args[0]:
                    diameter = int(args[0])
                else:
                    diameter = args[0]
            except ValueError:
                error = 'Invalid diameter argument %s ' % args[0]
            except TypeError:
                error = 'Expected a int or mapping key'

        if error is None:
            error = self._check_extra_args(lexer)

        return error, diameter, kw

    def _set_laser_power_parse(self, linenum, **kw):
        lexer = self._lexer
        error, args, kw = self._get_arguments(lexer)
        power = None
        if error is None:
            try:
                if '%' not in args[0]:
                    power = int(args[0])
                else:
                    power = args[0]

            except ValueError:
                error = 'Invalid power argument %s ' % args[0]
            except TypeError:
                error = 'Expected a int or mapping key'

        if error is None:
            error = self._check_extra_args(lexer)

        return error, power, kw

    def _device_parse(self, linenum, **kw):
        '''
            @type linenum: C{str}
            @param linenum:
        '''
        lexer = self._lexer
        error = None
        func = None
        device = None
        rargs = None
        rkw = dict()

        args = lexer.get_token()
        if not '.' in args:
            error = 'Invalid delimiter'
        elif args.endswith('.'):
            error = 'Specify a function to call'
        else:
            device, func = args.split('.')

            error, rargs, rkw = self._get_arguments(lexer)
            if error is None:
                error = self._check_extra_args(lexer)

        return error, device, func, rargs, rkw


    def _log_parse(self, linenum, **kw):
        '''
            @type linenum: C{str}
            @param linenum:
        '''
        lexer = self._lexer
        error = None
        msg = lexer.get_token()
        if not msg:
            error = 'Specify a message'
        else:
            msg = ' '.join([msg] + [l for l in lexer])
        return error, msg

    def _sub_parse(self, linenum, **kw):
        '''

        '''
        lexer = self._lexer
        error = None
        subpath = None
        subroutine = lexer.get_token()

        if not subroutine:
            error = 'Expected a subroutine'
        else:
            #check for valid subroutine
            subpath = self._check_valid_subroutine_(subroutine)
            if not subpath:

                error = 'Invalid subroutine %s' % subroutine

            else:
                self.script_name = subroutine
                with open(subpath, 'r') as f:
                    error = self.parse(f.read())
                    self.script_name = '-'

        error = [ei for ei in error if ei[2]]
#        print 'sub parse errr', error
        if not error:
            error = None

        return error, subpath

    def _valve_parse(self, linenum, **kw):
        '''
        ValveName.Action
        '''
        lexer = self._lexer
        error = None
        action = None
        valve_token = lexer.get_token()
        if '.' not in valve_token:
            error = 'Invalid syntax'
        elif valve_token.endswith('.'):
            error = 'Specify an action OPEN or CLOSE'
        else:
            valve_token, action = valve_token.split('.')
            if len(valve_token) > 1:
                error = 'Invalid valve name'
            if not action in VALID_ACTIONS:
                error = 'Invalid action %s' % action
            else:
                action = action in ['Open', 'OPEN', 'open']
                error = self._check_extra_args(lexer)
#                extra_args = lexer.get_token()
#                if extra_args:
#                    error = 'Extra args %s' % extra_args
        return error, valve_token, action


    def _wait_parse(self, linenum, **kw):
        '''
            
        '''
        return self._get_float()

    def _if_parse(self, linenum, **kw):
        '''
    
        '''
        lexer = self._lexer
        def _operator_(key, condition):

            try:
                l, r = condition.split(key)
                l = 'self.%s' % l
                try:
                    float(r)
                except ValueError:
                    if not "'" in r and r not in ['True', 'False']:
                        #assume quotes not apostrophe
                        r = 'self.%s' % r

                return ''.join((l, key, r))
            except ValueError:
                return condition

        def get_statement():

            statement = []
            else_ = False
            while 1:
                tok = lexer.get_token()
                if tok.lower() == 'else':
                    else_ = True
                    break
                elif tok == '':
                    break
                statement.append(tok)
            return ' '.join(statement), else_

        conditions = ['==', '!=', '<=', '>=', '<', '>']
        condition = lexer.get_token()
        cond_valid = False

        error = None
        true_statement = None
        false_statement = None
        for cond in conditions:
            if cond in condition and not condition.strip().endswith(cond):
                cond_valid = True
                break
        if condition:
            condition = _operator_(cond, condition)

        if not cond_valid:
            error = 'Invalid condition %s' % condition

        else:
            true_statement, else_ = get_statement()

            if true_statement:
                error = self._check_line(linenum, true_statement)[2]
            else:
                error = 'Specify a true statement'

            if error is None and else_:
                false_statement, else_ = get_statement()
                if false_statement:
                    error = self._check_line(linenum, false_statement)[2]
                else:
                    error = 'Specify a false statement'

        return error, condition, true_statement, false_statement

#============= views ===================================
#============= EOF ====================================
