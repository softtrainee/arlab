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
from traits.api import HasTraits, Property, Str, Float, Any, Int
from traitsui.api import View, Item, VGroup
from pyface.timer.api import Timer
#============= standard library imports ========================
import datetime
import time
#============= local library imports  ==========================

class ExperimentStats(HasTraits):
    elapsed = Property(depends_on='_elapsed')
    _elapsed = Float
    nruns = Int
    nruns_finished = Int
    etf = Str
    total_time = Property(depends_on='_total_time')
    _total_time = Float
    _timer = Any(transient=True)
    def calculate_etf(self, runs):
        self.nruns = len(runs)

        dur = sum([a.get_estimated_duration() for a in runs])
        self._total_time = dur

        dt = (datetime.datetime.now() + \
                       datetime.timedelta(seconds=int(dur)))
        self.etf = dt.strftime('%I:%M:%S %p %a %m/%d')

    def _get_total_time(self):
        dur = self._total_time
        return '{:0.3f} hrs ({} secs)'.format(dur / 3600., dur)

    def _get_elapsed(self):
        return str(datetime.timedelta(seconds=self._elapsed))

    def traits_view(self):
        v = View(VGroup(
                        Item('nruns',
                            label='Total Runs',
                            style='readonly'
                            ),
                        Item('nruns_finished',
                             label='Completed',
                             style='readonly'
                             ),
                        Item('total_time',
                              style='readonly'),
                        Item('etf', style='readonly', label='Est. finish'),
                        Item('elapsed',
                             style='readonly'),
                        )
                 )
        return v

    def start_timer(self):
        st = time.time()
        def update_time():
            self._elapsed = int(time.time() - st)

        self._timer = Timer(1000, update_time)
        self._timer.Start()

    def stop_timer(self):
        self._timer.Stop()
#============= EOF =============================================
