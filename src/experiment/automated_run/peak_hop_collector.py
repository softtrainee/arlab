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
import time
from traits.api import List, Int

#============= standard library imports ========================
#============= local library imports  ==========================
from src.experiment.automated_run.data_collector import DataCollector


class PeakHopCollector(DataCollector):
    hops = List
    settling_time = 0
    ncycles = Int

    def set_hops(self, hops):
        self.hops = hops
        self.debug('make new hop generatior')
        self.hop_generator = self._generator_hops()

    def _iter_hook(self, con, i):
        if i % 50 == 0:
            self.info('collecting point {}'.format(i))
        args = self._do_hop(i)
        if args:
            dets, isos = args
            # get the data
            data = self._get_data(dets)
            con.add_consumable((time.time() - self.starttime,
                                data, dets, isos, i))

    def _iter_step(self, data):
        x, data, dets, isos, i = data
        keys, signals = data

        self._plot_data(i, x, keys, signals)

    def _do_hop(self, cnt):
        """
            is it time for a magnet move
        """
        try:
            cycle, dets, isos, settle, move = self.hop_generator.next()
        except StopIteration:
            self.stop()
            return

        if cycle > self.plot_panel.ncycles:
            self.info('user termination. measurement iteration executed {} cycles'.format(cycle - 1, self.ncycles))
            self.stop()
            return
        else:
            if move:
                detector = dets[0]
                isotope = isos[0]

                #self.parent.set_magnet_position(isotope, detector, update_labels=False)
                msg = 'delaying {} for detectors to settle after peak hop'.format(settle)
                self.parent.wait(settle, msg)
                self.debug(msg)

        return dets, isos

    def _generator_hops(self):
        for c in xrange(self.ncycles):
            for hopstr, counts, settle in self.hops:
                his = hopstr.split(',')
                isos, dets = zip(*[map(str.strip, hi.split(':')) for hi in his])

                for i in xrange(int(counts)):
                    self.debug('cycle {} count {}'.format(c, i))
                    yield c, dets, isos, settle, i == 0


                    #def _measure2(self, evt):
                    #    graph=self.plot_panel.isotope_graph
                    #
                    #    original_idx = [(di.name, di.isotope) for di in self.detectors]
                    #
                    #    def idx_func(isot):
                    #        return next((i for i, (n, ii) in enumerate(original_idx)
                    #                            if ii == isot))
                    #
                    #    iter_count = 1
                    #    while 1:
                    #        ck = self._check_iteration(iter_count)
                    #        print ck
                    #        if ck == 'break':
                    #            break
                    #        elif ck == 'cancel':
                    #            return False
                    #
                    #        for hopstr, counts in self.hops:
                    #            if not self._alive:
                    #                return False
                    #
                    #            his = hopstr.split(',')
                    #            isos, dets = zip(*[map(str.strip, hi.split(':')) for hi in his])
                    #            #                dets = [hi.split(':')[1] for hi in  his]
                    #            #                dets = detstr.split(',')
                    #            #fits = [fi for fi, di in zip(self.fits,
                    #            #                             self.detectors)
                    #            #        if di.name in dets]
                    #
                    #            detector = dets[0]
                    #            isotope = isos[0]
                    #
                    #            self.parent._set_magnet_position(isotope, detector, update_labels=False)
                    #            time.sleep(self.settling_time)
                    #            for _ in xrange(int(counts)):
                    #                if not self._alive:
                    #                    return False
                    #
                    #                #if starttime is None:
                    #                    #starttime = time.time()
                    #
                    #                #x = time.time() - starttime
                    #                print self._get_data()
                    #                #data = spec.get_intensity(dets)
                    #                #if data is not None:
                    #                #    keys, signals = data
                    #                #else:
                    #                #    keys, signals = ('H2', 'H1', 'AX', 'L1', 'L2', 'CDD'), (1, 2, 3, 4, 5, 6)
                    #
                    #                #self.signals = dict(zip(dets, signals))
                    #                #print signals
                    #                #for signal, fi, iso in zip(signals, fits, isos):
                    #                #    pi = idx_func(iso)
                    #                #    if len(graph.series[pi]) < series + 1:
                    #                #        graph_kw = dict(marker='circle', type='scatter', marker_size=1.25)
                    #                #        func = lambda xi, yi, kw: graph.new_series(x=[xi],
                    #                #                                                   y=[yi],
                    #                #                                                   use_error_envelope=False,
                    #                #                                                   **kw
                    #                #        )
                    #                #    else:
                    #                #        graph_kw = dict(series=series,
                    #                #                        #                                             do_after=100,
                    #                #                        update_y_limits=True,
                    #                #                        ypadding='0.5')
                    #                #        func = lambda xi, yi, kw: graph.add_datum((xi, yi), **kw)
                    #                #
                    #                #    #                        print di, isotope, pi
                    #                #    graph_kw['plotid'] = pi
                    #                #    graph_kw['fit'] = fi
                    #                #    func(x, signal, graph_kw)
                    #                #
                    #                #data_write_hook(x, dets, signals)
                    #                #invoke_in_main_thread(graph._update_graph)
                    #                ##                     do_after(100, graph._update_graph)
                    #                time.sleep(self.period_ms/1000.)
                    #
                    #    return True

#============= EOF =============================================
