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
import shlex
import os
#============= local library imports  ==========================
from src.helpers import paths
from src.helpers.filetools import str_to_bool

RUNSCRIPT_DIR = os.path.join(paths.scripts_dir, 'runscripts')

LOW_PRIORITY_KEYS = ['FOR', ]

COMMAND_KEYS = ['LOG', 'VALVE', 'WAIT', 'SUB', 'IF', 'WARNING', 'DEVICE', 'MEASURE', 'MOVE_TO_HOLE',
                'ENABLE_LASER', 'DISABLE_LASER', 'SET_LASER_POWER', 'CLOSE_STAGE_MANAGER',
                'SET_BEAM_DIAMETER', 'SET_TIME_ZERO', 'CONFIG', 'DEFINE'
                ]
cl = [s.lower() for s in COMMAND_KEYS]
cc = [s.capitalize() for s in COMMAND_KEYS]
COMMAND_KEYS += cl + cc

VALID_ACTIONS = ['OPEN', 'CLOSE', 'Open', 'Close', 'open', 'close']

class ScriptParser(object):
    '''
        G{classtree}
    '''
    _errors_ = None
    script_name = ''
    def __init__(self):
        '''
        '''
        self._errors_ = []

    def set_lexer(self, text):
        '''

        '''
        self.lexer = shlex.shlex(text)
        self.lexer.wordchars += '.=!<>,%\''

    def get_command_token(self, cmd):
        '''
        '''
        lexer = self.lexer
        tok = lexer.get_token()
        if tok in COMMAND_KEYS:
            return tok

    def parse(self, text):
        '''
        '''
        errors = []
        if text is not None:
            if isinstance(text, str):
                text = text.split('\n')

            for linenum, line in enumerate(text):
                errors.append(self.__check_line__(linenum + 1, line.strip()))

        return errors

    def __get_subroutine_path__(self, subroutine):
        '''
            
        '''
        if '.' in subroutine:
            sub = RUNSCRIPT_DIR
            for b in subroutine.split('.'):
                sub = os.path.join(sub, b)
            subroutine = sub
            return os.path.join(RUNSCRIPT_DIR, '%s.rs' % subroutine)

    def __check_valid_subroutine__(self, subroutine):
        '''
            @type subroutine: C{str}
            @param subroutine:
        '''
        path = self.__get_subroutine_path__(subroutine.strip())

        if path and os.path.isfile(path):
            return path

    def __check_line__(self, linenum, line):
        '''
        '''
        self.set_lexer(line)

        token = self.lexer.get_token()
        error = None
        if token:
            if token in COMMAND_KEYS:
                try:
                    func = getattr(self, '__%s_parse__' % token.lower())
                    error = func(linenum)[0]
                except AttributeError:
                    pass
            else:
                error = 'Invalid KEY %s' % token
        return self.script_name, linenum, error

    #------------------------------------------------------------------- 
    #    parsers
    #------------------------------------------------------------------------------ 
    def __define_parse__(self, linenum):
        error = None
        lexer = self.lexer
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

    def __config_parse__(self, linenum):
        kw = dict()
        error = None
        if linenum != 1 and linenum != 0:
            error = 'config not at line 1'
        else:
            lexer = self.lexer
            token = lexer.get_token()
            while token:
                error = None
                if '=' not in token:
                    error = 'Expected ='
                else:
                    key, value = token.split('=')
                    if key == 'debug' and value:
                        bval = str_to_bool(value)
                        if bval is not None:
                            kw[key] = bval
                        else:
                            error = 'Expected boolean'

                token = self.lexer.get_token()
        return error, kw

    def __measure_parse__(self, linenum):
        '''
            @type linenum: C{str}
            @param linenum:
        '''
        lexer = self.lexer
        error = self._check_extra_args(lexer)

        return error, None
    def __warning_parse__(self, linenum):
        '''
            @type linenum: C{str}
            @param linenum:
        '''
        return self.__log_parse__(linenum)

    def __set_time_zero_parse__(self, linenum):
        lexer = self.lexer
        error, _args, _kw = self._get_arguments(lexer)
        if error is None:
            error = self._check_extra_args(lexer)
        return error,

    def __move_to_hole_parse__(self, linenum):
        lexer = self.lexer
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


    def __close_stage_manager_parse__(self, linenum):
        lexer = self.lexer
        error = self._check_extra_args(lexer)
        return error,

    def __enable_laser_parse__(self, linenum):
        lexer = self.lexer
        error = self._check_extra_args(lexer)
        return error,

    def __disable_laser_parse__(self, linenum):
        lexer = self.lexer
        error = self._check_extra_args(lexer)
        return error,

    def __set_beam_diameter_parse__(self, linenum):
        lexer = self.lexer
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

    def __set_laser_power_parse__(self, linenum):
        lexer = self.lexer
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

    def __device_parse__(self, linenum):
        '''
            @type linenum: C{str}
            @param linenum:
        '''
        lexer = self.lexer
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


    def __log_parse__(self, linenum):
        '''
            @type linenum: C{str}
            @param linenum:
        '''
        lexer = self.lexer
        error = None
        msg = lexer.get_token()
        if not msg:
            error = 'Specify a message'
        else:
            msg = ' '.join([msg] + [l for l in lexer])
        return error, msg

    def __sub_parse__(self, linenum):
        '''
            @type linenum: C{str}
            @param linenum:
        '''
        lexer = self.lexer
        error = None
        subpath = None
        subroutine = lexer.get_token()

        if not subroutine:
            error = 'Expected a subroutine'
        else:
            #check for valid subroutine
            subpath = self.__check_valid_subroutine__(subroutine)
            if not subpath:

                error = 'Invalid subroutine %s' % subroutine

            else:
                self.script_name = subroutine
                with open(subpath, 'r') as f:
                    error = self.parse(f.read())
                    self.script_name = '-'

        return error, subpath

    def __valve_parse__(self, linenum):
        '''
        ValveName.Action
        '''
        lexer = self.lexer
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

    def __wait_parse__(self, linenum):
        '''
            @type linenum: C{str}
            @param linenum:
        '''
        lexer = self.lexer
        error = None
        time = lexer.get_token()
        t = None
        if time:
            try:
                t = float(time)
            except ValueError:
                #see if this is a interpolation key
                if time[0] == '%':
                    t = time
                else:
                    error = 'Invalid float argument %s' % time

            error = self._check_extra_args(lexer)
#            extra_args = lexer.get_token()
#            if extra_args:
#                error = 'Extra args %s' % extra_args

        else:
            error = 'Specify a float or interpolation argument'

        return error, t

    def __if_parse__(self, linenum):
        '''
            @type linenum: C{str}
            @param linenum:
        '''
        lexer = self.lexer
        def _operator_(key, condition):

            try:
                l, r = condition.split(key)
                l = 'self.%s' % l
                try:
                    int(r)
                except ValueError:
                    if not "'" in r:
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
                error = self.__check_line__(linenum, true_statement)[2]
            else:
                error = 'Specify a true statement'

            if error is None and else_:
                false_statement, else_ = get_statement()
                if false_statement:
                    error = self.__check_line__(linenum, false_statement)[2]
                else:
                    error = 'Specify a false statement'

        return error, condition, true_statement, false_statement

    def _get_arguments(self, lexer):
        rargs = None
        rkw = dict()
        error = None
        lp = lexer.get_token()
        if lp:
            rargs = lexer.get_token()
            rp = lexer.get_token()
            if rp != ')':
                error = 'Expected )'
            else:
                rargs = rargs.split(',')
                for i, a in enumerate(rargs):
                    if '=' in a:
                        arg = rargs.pop(i)
                        rkw.update([arg.split('=')])
        return error, rargs, rkw
    def _check_extra_args(self, lexer):
        extra_args = lexer.get_token()
        if extra_args:
            return 'Extra args %s' % extra_args

#============= EOF ====================================
