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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
from src.spectrometer.tasks.magnet_scan import MagnetScan, psuedo_peak
from src.graph.graph import Graph
from globals import globalv
import time
import numpy as np
#============= standard library imports ========================
#============= local library imports  ==========================


class CoincidenceScan(MagnetScan):

    def _graph_hook(self, do, intensities, **kw):
        graph = self.graph
        if graph:
            spec = self.spectrometer
            for di, inte in zip(spec.detectors, intensities):
                lp = graph.plots[0].plot[di.name]
                ind = lp.index.get_data()
                ind = np.hstack((ind, do))
                lp.index.set_data(ind)

                val = lp.value.get_data()
                val = np.hstack((val, inte))
                lp.value.set_data(val)

    def _magnet_step_hook(self, di, peak_generator=None):

        spec = self.spectrometer
        intensities = spec.get_intensities()
#            debug
        if globalv.experiment_debug:
            inte = peak_generator.next()
            intensities = [inte * 1, inte * 2, inte * 3, inte * 4, inte * 5]

        return intensities

    def _graph_factory(self):
        g = Graph()
        g.new_plot()
        for di in self.spectrometer.detectors:
            g.new_series(
                         label=di.name,
                         color=di.color)

        return g

#============= EOF =============================================
