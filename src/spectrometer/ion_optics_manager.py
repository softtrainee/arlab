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
from traits.api import HasTraits, Range, Instance, Bool, Event, Property, Button, Any
from traitsui.api import View, Item, TableEditor
from src.managers.manager import Manager
from src.graph.graph import Graph
from src.spectrometer.peak_center import PeakCenter
from threading import Thread
#============= standard library imports ========================
#============= local library imports  ==========================

class IonOpticsManager(Manager):
    magnet_dac = Range(0.0, 6.0)
    graph = Instance(Graph)
    peak_center_button = Button('Peak Center')
    stop_button = Button('Stop')
    alive = Bool(False)
    spectrometer = Any

    def _peak_center(self):
        center_dac = 3
        reference_detector_name = 'AX'
        spec = self.spectrometer

        pc = PeakCenter(center_dac=center_dac,
                        reference_detector=reference_detector_name,
                        graph=self.graph,
                        magnet=spec.magnet
                        )

        npos = pc.get_peak_center()
        if npos:
            self.info('new center pos {}'.format(npos))
            spec.magnet.update_field_table(reference_detector_name, npos)

        else:
            self.warning_dialog('centering failed')
            self.warning('centering failed')

        self.alive = False

#===============================================================================
# handler
#===============================================================================
    def _peak_center_button_fired(self):

        t = Thread(name='ion_optics.peak_center', target=self._peak_center)
        t.start()

        self.alive = True

    def _stop_button_fired(self):
        self.alive = False

    def _graph_factory(self):
        g = Graph(container_dict=dict(padding=5, bgcolor='gray'))
        g.new_plot()
        return g

    def _graph_default(self):
        return self._graph_factory()

    def traits_view(self):
        v = View(Item('magnet_dac'),
                 Item('peak_center_button',
                      enabled_when='not alive',
                      show_label=False),
                 Item('stop_button', enabled_when='alive',
                       show_label=False),

                 Item('graph', show_label=False, style='custom'),


                  resizable=True)
        return v


if __name__ == '__main__':
    io = IonOpticsManager()
    io.configure_traits()

#============= EOF =============================================
