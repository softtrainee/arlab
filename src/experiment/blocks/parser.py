#===============================================================================
# Copyright 2012 Jake Ross
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
from src.constants import NULL_STR
from src.helpers.filetools import str_to_bool
#============= standard library imports ========================
#============= local library imports  ==========================
from src.loggable import Loggable
from src.regex import ALIQUOT_REGEX

class RunParser(Loggable):
    def parse(self, header, line, meta, delim='\t'):
        params = dict()
        if not isinstance(line, list):
            line = line.split(delim)

#        print len(line)
        args = map(str.strip, line)

        script_info = dict()
        # load scripts
        for attr in ['measurement', 'extraction',
                     'post_measurement',
                     'post_equilibration',
                     ]:
            try:
                script_info[attr] = args[header.index(attr)]
            except IndexError, e:
                self.debug('base schedule _run_parser {} {}'.format(e, attr))

        ln = args[header.index('labnumber')]
        if ALIQUOT_REGEX.match(ln):
            ln, a = ln.split('-')
            params['aliquot'] = int(a)

        params['labnumber'] = ln

        # load strings
        for attr in [
                     'measurement', 'extraction',
                     'post_measurement',
                     'post_equilibration',
                     'pattern',
                     'position',
                     'comment'
                     ]:
            try:
                params[attr] = args[header.index(attr)]
            except (IndexError, ValueError), e:
                self.debug('base schedule _run_parser {} {}'.format(e, attr))

        # load booleans
        for attr in ['autocenter', 'disable_between_positions']:
            try:
                param = args[header.index(attr)]
                if param.strip():
                    bo = str_to_bool(param)
                    if bo is not None:
                        params[attr] = bo
                    else:
                        params[attr] = False
            except (IndexError, ValueError):
                params[attr] = False

        # load numbers
        for attr in ['duration', 'overlap', 'cleanup',
#                     'aliquot',
                     'extract_group',
                     'weight'
                     ]:
            try:
                param = args[header.index(attr)].strip()
                if param:
                    params[attr] = float(param)
            except (IndexError, ValueError):
                pass

        # default extract_units to watts
#        print header.index('extract_value'), len(args)
        extract_value = args[header.index('extract_value')]
        extract_units = args[header.index('extract_units')]
        if not extract_units:
            extract_units = '---'

        params['extract_value'] = extract_value
        params['extract_units'] = extract_units

#        def make_script_name(n):
#            try:
#                na = args[header.index(n)]
#                if na.startswith('_'):
#                    if meta:
#                        na = meta['mass_spectrometer'] + na
#
#                if na and not na.endswith('.py'):
#                    na = na + '.py'
#            except IndexError, e:
#                print 'base schedule make_script_name ', e
#                na = NULL_STR
#
#            return na

        return script_info, params  # , make_script_name


class UVRunParser(RunParser):
    def parse(self, header, line, meta, delim='\t'):
        params = super(UVRunParser, self).parse(header, line, meta, delim)
        if not isinstance(line, list):
            line = line.split(delim)

        args = map(str.strip, line)

        def _set(attr, cast):
            try:
                v = args[header.index(attr)]
                params[attr] = cast(v)
            except (IndexError, ValueError, TypeError):
                pass

        _set('reprate', int)
        _set('attenuator', str)
        _set('mask', str)
        _set('image', str)

        return params
#============= EOF =============================================
