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
from traits.api import HasTraits, Any, List, CInt, Str, Int
from traitsui.api import View, Item
from pyface.timer.do_later import do_after
#============= standard library imports ========================
import time
from threading import Event
from numpy import Inf
#============= local library imports  ==========================
from src.loggable import Loggable
from src.ui.gui import invoke_in_main_thread
from src.globals import globalv
from src.consumer_mixin import consumable

class DataCollector(Loggable):
    measurement_script = Any
    plot_panel = Any
    detectors = List
    truncation_conditions = List
    terminations_conditions = List
    action_conditions = List
    ncounts = CInt
    grpname = Str
    fits = List
    series_idx = Int
    total_counts = CInt

    canceled=False
    
    _truncate_signal = False
    starttime = None
    _alive = False
    _evt=None
    def set_truncated(self):
        self._truncate_signal = True

    def stop(self):
        self._alive = False
        if self._evt:
            self._evt.set()
            
    def measure(self):
        if self.canceled:
            return
        
        self._truncate_signal = False

        st = time.time()
        if self.starttime is None:
            self.starttime = st

        et = self.ncounts * self.period_ms * 0.001
        evt = Event()
        self._evt=evt
        with consumable(func=self._iter_step) as con:
            self._alive = True
            invoke_in_main_thread(self._iter, con, evt, 1)
            evt.wait(et * 1.1)

        tt = time.time() - st
        self.debug('estimated time: {:0.3f} actual time: :{:0.3f}'.format(et, tt))
        return self.total_counts

    def _iter(self, con, evt, i, prev=0):
        ct = time.time()
        x = ct - self.starttime
        if not self._check_iteration(i):
            # get the data
            data = self._get_data()
#             self._iter_step((x, data, i))
            con.add_consumable((x, data, i))

            p = self.period_ms
            p -= prev * 1000

            p = max(1, p)
            do_after(p, self._iter, con, evt, i + 1, prev=time.time() - ct)

        else:
            evt.set()

    def _iter_step(self, data):
        x, data, i = data

        # save the data
        self._save_data(x, *data)
        # plot the data
        self._plot_data(i, x, *data)

    def _get_data(self):
        return self.data_generator.next()

    def _save_data(self, x, keys, signals):
        self.data_writer(self.detectors, x, keys, signals)


    def _plot_data(self, i, x, keys, signals):
        if globalv.experiment_debug:
            x *= (self.period_ms * 0.001) ** -1
        dets = self.detectors
        graph = self.plot_panel.isotope_graph

        nfs = self.get_fit_block(i)
        if self.grpname == 'signal':
            self.plot_panel.fits = nfs

        for pi, (fi, dn) in enumerate(zip(nfs, dets)):
            signal = signals[keys.index(dn.name)]
            graph.add_datum((x, signal),
                            series=self.series_idx,
                            plotid=pi,
                            update_y_limits=True,
                            ypadding='0.1'
                            )
            if fi:
                graph.set_fit(fi, plotid=pi, series=0)
        graph.refresh()

#===============================================================================
#
#===============================================================================
    def get_fit_block(self, iter_cnt, fits=None):
        if fits is None:
            fits = self.fits
        return self._get_fit_block(iter_cnt, fits)

    def _get_fit_block(self, iter_cnt, fits):
        for sli, fs in fits:
            if sli:

                s, e = sli
                if s is None:
                    s = 0
                if e is None:
                    e = Inf

                if iter_cnt > s and iter_cnt < e:
                    break

#        self.debug('fs {}'.format(fs))
        return fs
#===============================================================================
# checks
#===============================================================================
    def _check_conditions(self, conditions, cnt):
        for ti in conditions:
            if ti.check(self.arar_age, cnt):
                return ti

    def _check_iteration(self, i):

#         if self.plot_panel is None:
#             return 'break'
        if self._evt:
            if self._evt.isSet():
                return True
            
        j = i - 1
        # exit the while loop if counts greater than max of original counts and the plot_panel counts
        pc = 0
        if self.plot_panel:
            pc = self.plot_panel.ncounts

        ncounts = self.ncounts
        maxcounts = max(ncounts, pc)
#         print i, maxcounts
        if i > maxcounts:
            return 'break'

        if self.check_conditions:
            termination_condition = self._check_conditions(self.termination_conditions, i)
            if termination_condition:
                self.info('termination condition {}. measurement iteration executed {}/{} counts'.format(termination_condition.message, j, ncounts),
                          color='red'
                          )
                return 'cancel'

            truncation_condition = self._check_conditions(self.truncation_conditions, i)
            if truncation_condition:
                self.info('truncation condition {}. measurement iteration executed {}/{} counts'.format(truncation_condition.message, j, ncounts),
                          color='red'
                          )
                self.state = 'truncated'
                self.measurement_script.abbreviated_count_ratio = truncation_condition.abbreviated_count_ratio

#                self.condition_truncated = True
                return 'break'

            action_condition = self._check_conditions(self.action_conditions, i)
            if action_condition:
                self.info('action condition {}. measurement iteration executed {}/{} counts'.format(action_condition.message, j, ncounts),
                          color='red'
                          )
                action_condition.perform(self.measurement_script)
                if not action_condition.resume:
                    return 'break'

        if i > self.measurement_script.ncounts:
            self.info('script termination. measurement iteration executed {}/{} counts'.format(j, ncounts))
            return 'break'

        if pc:
            if i > pc:
                self.info('user termination. measurement iteration executed {}/{} counts'.format(j, ncounts))
                self.total_counts -= (ncounts - i)
                return 'break'

        if self._truncate_signal:
            self.info('measurement iteration executed {}/{} counts'.format(j, ncounts))
            self._truncate_signal = False

            return 'break'

        if not self._alive:
            self.info('measurement iteration executed {}/{} counts'.format(j, ncounts))
            return 'cancel'
#============= EOF =============================================
