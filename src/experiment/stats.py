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
from traits.api import Property, Str, Float, Any, Int, List
from traitsui.api import View, Item, VGroup
from pyface.timer.api import Timer
#============= standard library imports ========================
import datetime
import time
from src.loggable import Loggable
#============= local library imports  ==========================


class ExperimentStats(Loggable):
    elapsed = Property(depends_on='_elapsed')
    _elapsed = Float
    nruns = Int
    nruns_finished = Int
    etf = Str
    time_at = Str
    total_time = Property(depends_on='_total_time')
    _total_time = Float
    _timer = Any(transient=True)
    delay_between_analyses = Float
    _start_time = None
    experiment_set = Any

    def calculate_duration(self, runs=None):
        if runs is None:
            runs = self.experiment_set.cleaned_automated_runs
        dur = self._calculate_duration(runs)
        self._total_time = dur
        return dur

    def calculate_etf(self):
        runs = self.experiment_set.cleaned_automated_runs
        dur = self._calculate_duration(runs)
        self._total_time = dur
        self.etf = self.format_duration(dur)

    def format_duration(self, dur):
        dt = (datetime.datetime.now() + \
                       datetime.timedelta(seconds=int(dur)))
        return dt.strftime('%I:%M:%S %p %a %m/%d')

    def _calculate_duration(self, runs):
        ni = len(runs)
        dur = sum([a.get_estimated_duration() for a in runs])
        dur += (self.delay_between_analyses * ni)
        return dur

    def _get_total_time(self):
        dur = datetime.timedelta(seconds=round(self._total_time))
        return str(dur)

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
                        Item('time_at', style='readonly'),
                        Item('etf', style='readonly', label='Est. finish'),
                        Item('elapsed',
                             style='readonly'),
                        )
                 )
        return v

    def start_timer(self):
        st = time.time()
        self._start_time = st
        def update_time():
            self._elapsed = round(time.time() - st)

        self._timer = Timer(500, update_time)
        self._timer.Start()

    def stop_timer(self):
        tt = self._total_time
        et = self._elapsed
        dt = tt - et
        self.info('Estimated total time= {:0.1f}, elapsed time= {:0.1f}, deviation= {:0.1f}'.format(tt, et, dt))
        self._timer.Stop()

    def reset(self):
        self._start_time = None
        self.nruns_finished = 0

class StatsGroup(ExperimentStats):
    experiment_sets = List
    def calculate(self):
        ''' 
            calculate the total duration
            calculate the estimated time of finish
        '''

        runs = [ai
                for ei in self.experiment_sets
                    for ai in ei.cleaned_automated_runs]
        ni = len(runs)
        self.nruns = ni
        tt = sum([ei.stats.calculate_duration()
                 for ei in self.experiment_sets])
        self._total_time = tt
        offset = 0
        if self._start_time:
            offset = time.time() - self._start_time

        self.etf = self.format_duration(tt - offset)

    def calculate_at(self, sel):
        '''
            calculate the time at which a selected run will execute
        '''
        tt = 0
        for ei in self.experiment_sets:
            if sel in ei.cleaned_automated_runs:
                si = ei.cleaned_automated_runs.index(sel)
                tt += ei.stats.calculate_duration(ei.cleaned_automated_runs[:si + 1])
                break
            else:
                tt += ei.stats.calculate_duration()

        self.time_at = self.format_duration(tt)



#============= EOF =============================================
