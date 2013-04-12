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
from traits.api import HasTraits, Int
from traitsui.api import View, Item, TableEditor, Group
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.pyscripts.pyscript_editor import PyScriptManager
from src.paths import paths

import re
MULTICOLLECT_NCOUNTS_REGEX = re.compile(r'(MULTICOLLECT_COUNTS) *= *\d+$')
BASELINE_NCOUNTS_REGEX = re.compile(r'(BASELINE_COUNTS) *= *\d+$')

class MeasurementPyScriptManager(PyScriptManager):
    kind = 'Measurement'

    multicollect_ncounts = Int(100)
    baseline_ncounts = Int(100)
    def _get_design_group(self):

        multicollect_grp = Group(
                                 Item('multicollect_ncounts', label='Counts'),
                                 label='Multicollect',
                                 show_border=True
                                 )
        baseline_grp = Group(
                                 Item('baseline_ncounts', label='Counts'),
                                 label='Baseline',
                                 show_border=True
                                 )
        return Group(
                     multicollect_grp,
                     baseline_grp,
                     label='Design')

    def _parse(self):
        for li in self.body.split('\n'):
            self._extract_parameter(li, MULTICOLLECT_NCOUNTS_REGEX, 'multicollect_ncounts', cast=int)
            self._extract_parameter(li, BASELINE_NCOUNTS_REGEX, 'baseline_ncounts', cast=int)

    def _extract_parameter(self, line, regex, attr, cast=None):
        if regex.match(line):
            _, v = line.split('=')
            if cast:
                v = cast(v)
            setattr(self, attr, v)

    def _multicollect_ncounts_changed(self):
        regex = MULTICOLLECT_NCOUNTS_REGEX
        nv = 'MULTICOLLECT_COUNTS= {}'.format(self.multicollect_ncounts)
        self._modify_body(regex, nv)

    def _baseline_ncounts_changed(self):
        regex = BASELINE_NCOUNTS_REGEX
        nv = 'BASELINE_COUNTS= {}'.format(self.baseline_ncounts)
        self._modify_body(regex, nv)

    def _modify_body(self, regex, nv):
        ostr = []
        for li in self.body.split('\n'):
            if regex.match(li):
                ostr.append(nv)
            else:
                ostr.append(li)

        self.body = '\n'.join(ostr)



if __name__ == '__main__':
    from launchers.helpers import build_version
    build_version('_experiment')
    from src.helpers.logger_setup import logging_setup
    logging_setup('scripts')
#    s = PyScriptManager(kind='ExtractionLine')
#    s = PyScriptManager(kind='Bakeout')
    s = MeasurementPyScriptManager(kind='Measurement')

    p = os.path.join(paths.scripts_dir, 'measurement', 'jan_unknown.py')
    s.open_script(path=p)
    s.configure_traits()
#============= EOF =============================================
