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
from src.helpers.filetools import str_to_bool

#============= local library imports  ==========================
class CoreScriptParser(object):
    COMMAND_KEYS = ['----']

    _lexer = None
    script_name = ''

    headerindex = None

    def _header_parse(self, linenum, **kw):
        self.headerindex = linenum
        return None,

    def set_lexer(self, text):
        '''

        '''
        self._lexer = shlex.shlex(text)
        self._lexer.wordchars += '.=!<>,%\'-'

    def _get_command_keys(self):
        ck = self.COMMAND_KEYS
        cl = [s.lower() for s in ck]
        cc = [s.capitalize() for s in ck]

        return ck + cl + cc

    def get_command_token(self):
        '''

        '''
        tok = self.get_token()
        if '----' in tok or tok in self._get_command_keys():
            return tok

    def get_token(self):
        return self._lexer.get_token()

    def parse(self, text, **kw):
        '''

        '''

        errors = []
        if text is not None:

            if isinstance(text, str):
                text = text.split('\n')

            self.text = text
            for linenum, line in enumerate(text):
                errors.append(self._check_line(linenum + 1, line.strip()))

        return errors

    def _raw_parse(self, linenum, line=None):
        if line is None:
            line = self.text[linenum - 1]

        args = line.split(',')
        return self.raw_parse(args)

    def _config_parse(self, linenum, **kw):
        kw = dict()
        error = None
        if linenum != 1 and linenum != 0:
            error = 'config not at line 1'
        else:
            lexer = self._lexer
            token = lexer.get_token()
            while token:
                error = None
                if '=' not in token:
                    error = 'Expected ='
                else:
                    key, value = token.split('=')
                    bval = str_to_bool(value)
                    if key == 'debug' and value:
                        if bval is not None:
                            kw[key] = bval
                        else:
                            error = 'Expected boolean'
                    else:
                        if bval is None:
                            kw[key] = value
                        else:
                            kw[key] = bval

                token = self._lexer.get_token()

        return error, kw

    def _get_float(self):
        lexer = self._lexer
        error = None
        ti = lexer.get_token()
        print 'getfloat', ti
        t = None
        if ti:
            try:
                t = float(ti)
            except ValueError:
                #see if this is a interpolation key
                if ti[0] == '%':
                    t = self._get_interpolation_value(ti)
                else:
                    error = 'Invalid float argument {}'.ti

            error = self._check_extra_args(lexer)

        else:
            error = 'Specify a float or interpolation argument'



        return error, t

    def _get_str(self):
        lexer = self._lexer
        ti = lexer.get_token()
        error = self._check_extra_args(lexer)
        return error, ti

    def _get_int(self):
        lexer = self._lexer
        error = None
        ti = lexer.get_token()
        t = None
        if ti:
            try:
                t = int(ti)
            except ValueError:
                #see if this is a interpolation key
                if ti[0] == '%':
                    t = ti
                else:
                    error = 'Invalid int argument {}'.ti

            error = self._check_extra_args(lexer)

        else:
            error = 'Specify a int or interpolation argument'

        return error, t

    def _check_float(self, n):
        err = None
        try:
            n = float(n)
        except (ValueError, AttributeError):
            err = 'Invalid float arg {}'.format(n)

        return err, n

    def _check_number(self, args):
        errora = []
        error = None
        for a in args:
            try:
                a = float(a)
            except ValueError:
                errora.append(a)
        if errora:
            error = 'Invalid args %s' % ','.join(errora)
        return error

    def raw_parse(self, *args):
        return 'Raw line not allowed',

    def _check_line(self, linenum, line):
        '''

        '''
        self.set_lexer(line)

        token = self._lexer.get_token()
        error = None
        if token:
            if not token in self._get_command_keys():
                try:
                    float(token)
                    token = 'raw'
                except ValueError:
                    if not ',' in token:
                        error = 'Invalid KEY {}'.format(token)
                    else:
                        token = 'raw'

            if '----' in token:
                token = 'header'

            if not error:
                try:
                    func = getattr(self, '_{}_parse'.format(token.lower()))
                    error = func(linenum)[0]
                except AttributeError:
                    pass

        return self.script_name, linenum, error

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

    def _to_bool(self, arg):
        return True if arg in ['True', 'T', 'true', 't', '1'] else False

    def _get_interpolation_value(self, key):
        value = 0
        if self.script is not None:

            if key[0] == '%':
                key = key[1:]

            try:
                value = getattr(self.script, key)
            except AttributeError, e:
                self.warning_statement(e)

        self.log_statement('Interpolated value for %s = %s' % (key, value))
        return value
#============= views ===================================
#============= EOF ====================================
