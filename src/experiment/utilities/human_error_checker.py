#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits
from traitsui.api import View, Item
from src.loggable import Loggable
from src.experiment.utilities.identifier import get_analysis_type
from src.constants import NULL_STR, LINE_STR
#============= standard library imports ========================
#============= local library imports  ==========================

class HumanErrorChecker(Loggable):
    _extraction_line_required = False
    _mass_spec_required = False

    def check_queue(self, qi):
        self.info('check queue {}'.format(qi.name))
        if self._extraction_line_required:
            if not qi.extract_device or \
                qi.extract_device in ('Extract Device', LINE_STR):
                self.info('no extraction line')
                return 'no extraction line'

        if self._mass_spec_required:
            if not qi.mass_spectrometer or \
                qi.mass_spectrometer in ('Spectrometer', LINE_STR):
                self.info('no mass spectrometer')
                return 'no mass spectrometer'

    def check_runs(self, runs, test_all=False, inform=True):
        ret = dict()

        inform = inform and not test_all
        for i, ai in enumerate(runs):
            err = self._check_run(ai, inform)
            if err is not None:
                ai.state = 'invalid'
                ret[ai.runid] = err
                if not test_all:
                    return ret
            else:
                ai.state = 'not run'

        return ret

    def report_errors(self, errdict):

        msg = '\n'.join(['{} {}'.format(k, v) for k, v in errdict.iteritems()])
        self.warning_dialog(msg)

    def check_run(self, run, inform=True):
        return self._check_run(run, inform)

    def _check_run(self, run, inform):

        err = self._check_attr(run, 'labnumber', inform)
        if err is not None:
            return err

        ant = get_analysis_type(run.labnumber)
        if ant == 'unknown':
            for attr in ('duration', 'cleanup'):
                err = self._check_attr(run, attr, inform)
                if err is not None:
                    return err

            if run.position:
                if not run.extract_value:
                    return 'position but no extract value'

        if ant in ('unknown', 'background') or ant.startswith('blank'):
            self._mass_spec_required = True

        if run.extract_value or run.cleanup or run.duration:
            self._extraction_line_required = True

    def _check_attr(self, run, attr, inform):
        if not getattr(run, attr):
            msg = 'No {} set for {}'.format(attr, run.runid)
            self.warning(msg)
            if inform:
                self.warning_dialog(msg)
            return 'no {}'.format(attr)

#============= EOF =============================================
