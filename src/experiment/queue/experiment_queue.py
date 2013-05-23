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
from traits.api import HasTraits, Any, Button, on_trait_change
from traitsui.api import View, Item, TableEditor
from src.experiment.queue.base_queue import BaseExperimentQueue
from src.constants import SCRIPT_KEYS, SCRIPT_NAMES
from src.experiment.utilities.identifier import make_runid
#============= standard library imports ========================
#============= local library imports  ==========================

class ExperimentQueue(BaseExperimentQueue):
    _cached_runs = None
    current_run = Any
    selected = Any
    refresh_button = Button('Refresh')
    dclicked = Any

    def copy_function(self, obj):
        ci = obj.clone_traits()
        ci.state = 'not run'
        return ci

    @on_trait_change('automated_runs[]')
    def _refresh_info(self, new):
        if not self._no_update:
            self.debug('automated runs len changed {}'.format(len(new)))
            if self.automated_runs:
                self.refresh_button = True

    def test_runs(self):
#         self.executable=True
        runs = self.cleaned_automated_runs

        tested = []
        if runs:
            ar = runs[0].make_run()
            self.executable = False
            for ri in runs:
                for si in SCRIPT_NAMES:
                    sn = getattr(ri, si)
                    if not sn in tested:
                        setattr(ar.script_info, '{}_name'.format(si), sn)
                        script = getattr(ar, si)
                        if script is not None:
                            tested.append(sn)
                            if not script.syntax_ok():
                                return 'Error in script {}'.format(script.name)

        self.executable = True

    def new_runs_generator(self, last_ran=None):
        runs = self.cleaned_automated_runs

        runs = [ri for ri in runs if ri.executable]

        n = len(runs)
        rgen = (r for r in runs)
        if last_ran is not None:
            # get index of last run in self.automated_runs
            if self._cached_runs:
                startid = self._cached_runs.index(last_ran) + 1
                # for graphic clarity load the finished runs back in
#                cnts = {}
                for ci, ai in zip(self._cached_runs[:startid], runs[:startid]):
                    ai.trait_set(state=ci.state, aliqupt=ci.aliquot,
                                 step=ci.step,
                                 skip=ci.skip)

#                for ai in self.automated_runs:
#                    if ai.skip:
#                        continue
#                    crun = next((r for r in cached if r.labnumber == ai.labnumber), None)
#                    if crun is not None:
#                        ai.state = crun.state
#                        cnt = 0
#                        if ai.labnumber in cnts:
#                            cnt = cnts[ai.labnumber] + 1
#
#                        ai.aliquot = crun.aliquot + cnt
#                        cnts[ai.labnumber] = cnt
#                        print 'setting ', crun.aliquot

                newruns = runs[startid:]

                run = newruns[0]
#                runid = run.runid
                runid = make_runid(run.labnumber, run.aliquot, run.step)

                self.info('starting at analysis {} (startid={} of {})'.format(runid, startid + 1, n))
                n = len(newruns)
                rgen = (r for r in newruns)
            else:
                self.info('last ran analysis {} does not exist in modified experiment set. starting from the beginning')

        return rgen, n

#============= EOF =============================================
