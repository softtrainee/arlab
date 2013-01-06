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
from traits.api import Float
#============= standard library imports ========================
from numpy import array, max, polyfit, argmax
#============= local library imports  ==========================
from magnet_scan import MagnetScan
from src.graph.graph import Graph

def calculate_peak_center(x, y, min_peak_height=1.0, percent=80):
        x = array(x)
        y = array(y)

        ma = max(y)
        max_i = argmax(y)

        if ma < min_peak_height:
            return 'No peak greater than {}. max = {}'.format(min_peak_height, ma)

        mx = x[max_i]
        my = ma

        #look backward for point that is peak_percent% of max
        for i in range(max_i, max_i - 50, -1):
            #this prevent looping around to the end of the list
            if i < 1:
                return 'PeakCenterError: could not find a low pos'


            try:
                if y[i] < (ma * (1 - percent / 100.)):
                    break
            except IndexError:
                return 'PeakCenterError: could not find a low pos'

        xstep = (x[i] - x[i - 1]) / 2.
        lx = x[i] - xstep
        ly = y[i] - (y[i] - y[i - 1]) / 2.

        #look forward for point that is 80% of max
        for i in range(max_i, max_i + 50, 1):
            try:
                if y[i] < (ma * (1 - percent / 100.)):
                    break
            except IndexError:
                return 'PeakCenterError: could not find a high pos'

        try:
            hx = x[i + 1] - xstep
            hy = y[i] - (y[i] - y[i + 1]) / 2.
        except IndexError:
            return 'peak not well centered'

        if (hx - lx) < 0:
            return 'unable to find peak bounds high_pos < low_pos. {} < {}'.format(hx, lx)

        cx = (hx + lx) / 2.0
        cy = ma

        #find index in x closest to cx
        ccx = abs(x - cx).argmin()
        #check to see if were on a plateau
        yppts = y[ccx - 2:ccx + 2]

        slope, _ = polyfit(range(len(yppts)), yppts, 1)
        std = yppts.std()

        if std > 5 and abs(slope) < 1:
            return 'No peak plateau std = {} (>5) slope = {} (<1)'.format(std, slope)
#        else:
#            self.info('peak plateau std = {} slope = {}'.format(std, slope)

        return [lx, cx, hx ], [ly, cy, hy], mx, my



class PeakCenter(MagnetScan):
    center_dac = Float

    window = Float(0.015)
    step_width = Float(0.0005)
    min_peak_height = Float(1.0)
    canceled = False

#    data = None
    result = None
    directions = None

    def get_peak_center(self, ntries=2):
        self._alive = True
        graph = self.graph
        center_dac = self.center_dac
        self.info('starting peak center. center dac= {}'.format(center_dac))

        for i in range(ntries):
            if not self.isAlive():
                break

            if i > 0:
                graph.clear()
                self._graph_factory(graph=graph)

            wnd = self.window

            start = center_dac - wnd * (i + 1)
            end = center_dac + wnd * (i + 1)
            self.info('Scan parameters center={} start={} end={} step width={}'.format(center_dac, start, end, self.step_width))
            graph.set_x_limits(min=min([start, end]), max=max([start, end]))

            width = self.step_width
            try:
                if self.simulation:
                    width = 0.001
            except AttributeError:
                width = 0.001

#            print center_dac + 0.001, start, end, nsteps
#            intensities = self._scan_dac(dac_values, self.detector)
#            self.data = (dac_values, intensities)        
            ok = self._do_scan(start, end, width, directions=self.directions, map_mass=False)
            if ok and self.directions != 'Oscillate':
                if not self.canceled:
                    dac_values = graph.get_data()
                    intensities = graph.get_data(axis=1)

                    n = zip(dac_values, intensities)
                    n = sorted(n, key=lambda x: x[0])
                    dac_values, intensities = zip(*n)

#                    self.data = (dac_values, intensities)
                    result = self._calculate_peak_center(dac_values, intensities)
                    self.result = result
                    if result is not None:

                        xs, ys, mx, my = result

                        center = xs[1]
                        graph.set_data(xs, series=1)
                        graph.set_data(ys, series=1, axis=1)

                        graph.set_data([mx], series=2)
                        graph.set_data([my], series=2, axis=1)

                        graph.add_vertical_rule(center)
                        graph.redraw()
                        return center

    def _calculate_peak_center(self, x, y):
        result = calculate_peak_center(x, y,
                                       min_peak_height=self.min_peak_height,
                                       )
        if result is not None:
            if isinstance(result, str):
                self.warning(result)
            else:
                return result
#        peak_threshold = self.min_peak_height
#        peak_percent = 0.8
#
#        x = array(x)
#        y = array(y)
#
#        ma = max(y)
#        max_i = argmax(y)
#
#        if ma < peak_threshold:
#            self.warning('No peak greater than {}. max = {}'.format(peak_threshold, ma))
#            return
#
#        mx = x[max_i]
#        my = ma
#
#        #look backward for point that is peak_percent% of max
#        for i in range(max_i, max_i - 50, -1):
#            #this prevent looping around to the end of the list
#            if i < 1:
#                self.warning('PeakCenterError: could not find a low pos')
#                return
#
#            try:
#                if y[i] < (ma * (1 - peak_percent)):
#                    break
#            except IndexError:
#                '''
#                could not find a low pos
#                '''
#                self.warning('PeakCenterError: could not find a low pos')
#                return
#
#        xstep = (x[i] - x[i - 1]) / 2.
#        lx = x[i] - xstep
#        ly = y[i] - (y[i] - y[i - 1]) / 2.
#
#        #look forward for point that is 80% of max
#        for i in range(max_i, max_i + 50, 1):
#            try:
#                if y[i] < (ma * (1 - peak_percent)):
#                    break
#            except IndexError:
#                '''
#                    could not find a high pos
#                '''
#                self.warning('PeakCenterError: could not find a high pos')
#                return
#        try:
#            hx = x[i + 1] - xstep
#            hy = y[i] - (y[i] - y[i + 1]) / 2.
#        except IndexError:
#            self.warning('peak not well centered')
#            return
#
#        if (hx - lx) < 0:
#            self.warning('unable to find peak bounds high_pos < low_pos. {} < {}'.format(hx, lx))
#            return
#
#        cx = (hx + lx) / 2.0
#        cy = ma
#
#        #find index in x closest to cx
#        ccx = abs(x - cx).argmin()
#        #check to see if were on a plateau
#        yppts = y[ccx - 2:ccx + 2]
#
#        slope, _ = polyfit(range(len(yppts)), yppts, 1)
#        std = yppts.std()
#
#        if std > 5 and abs(slope) < 1:
#            self.warning('No peak plateau std = {} slope = {}'.format(std, slope))
#            return
#        else:
#            self.info('peak plateau std = {} slope = {}'.format(std, slope))
#
#        return [lx, cx, hx ], [ly, cy, hy], mx, my

#===============================================================================
# factories
#===============================================================================
    def _graph_factory(self, graph=None):
        if graph is None:
            graph = Graph(
                  container_dict=dict(padding=5,
                                      bgcolor='lightgray'))

        graph.new_plot(
                       padding=[50, 5, 5, 50],
#                       title='{}'.format(self.title),
                       xtitle='DAC (V)',
                       ytitle='Intensity (fA)',
                       )

        graph.new_series(type='scatter', marker='circle',
                         marker_size=1.25
                         )
        graph.new_series(type='scatter', marker='circle',
                         marker_size=4
                         )
        graph.new_series(type='scatter', marker='circle',
                         marker_size=4,
                         color='green'
                         )

        graph.plots[0].value_range.tight_bounds = False
        return graph

#    def _peak_center_graph_factory(self, graph, start, end, title=''):
#        graph.container_dict = dict(padding=[10, 0, 30, 10])
#        graph.clear()



#============= EOF =============================================
#        '''
#            center pos needs to be ne axial dac units now
#        '''
#        if isinstance(center_pos, str):
#            '''
#                passing in a mol weight key ie Ar40
#                get_dac_for_mass can take a str or a float 
#                if str assumes key else assumes mass
#            '''
#            center_pos = self.magnet.get_dac_for_mass(center_pos)
#
#        if center_pos is None:
#            #center at current position
#            center_dac = self.magnet.read_dac()
#            if isinstance(center_dac, str) and 'ERROR' in center_dac:
#                center_dac = 6.01
#        else:
#            center_dac = center_pos

#        ntries = 2
#        success = False
#        result = None

