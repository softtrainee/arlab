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

#============= standard library imports ========================
import shlex

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
            @type text: C{str}
            @param text:
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
            @type cmd: C{str}
            @param cmd:
        '''
        tok = self.get_token()
        if '----' in tok or tok in self._get_command_keys():
            return tok

    def get_token(self):
        return self._lexer.get_token()

    def parse(self, text, **kw):
        '''
            @type text: C{str}
            @param text:
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
            @type linenum: C{str}
            @param linenum:

            @type line: C{str}
            @param line:
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
                        error = 'Invalid KEY %s' % token
                    else:
                        token = 'raw'

            if '----' in token:
                token = 'header'

            if not error:
                try:
                    func = getattr(self, '_%s_parse' % token.lower())
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
#============= views ===================================
#============= EOF ====================================
