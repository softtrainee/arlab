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
from src.spectrometer.tasks.peak_center import PeakCenter
from threading import Thread
from pyface.timer.do_later import do_later
#============= standard library imports ========================
#============= local library imports  ==========================

class IonOpticsManager(Manager):
    magnet_dac = Range(0.0, 6.0)
    graph = Instance(Graph)
    peak_center_button = Button('Peak Center')
    stop_button = Button('Stop')
    alive = Bool(False)
    spectrometer = Any

    peak_center = Instance(PeakCenter)
    canceled = False

    def do_peak_center(self, save=True, confirm_save=False):
        spec = self.spectrometer

        self.canceled = False
        self.alive = True

        t = Thread(name='ion_optics.peak_center', target=self._peak_center,
                   args=(spec.magnet.dac, save, confirm_save))
        t.start()

    def _peak_center(self, center_dac, save, confirm_save):
        graph = self._graph_factory()

        #set graph window attributes
        graph.window_title = 'Peak Center @ {:0.3f}'.format(center_dac)

        #bind to the graphs close_func
        #self.close is called when graph window is closed
        #use so we can stop the timer
        graph.close_func = self.close

        self.open_view(graph)

        reference_detector_name = 'AX'
        reference_isotope_name = 'Ar40'
        spec = self.spectrometer

        self.peak_center = pc = PeakCenter(center_dac=center_dac,
                        reference_isotope=reference_detector_name,
                        graph=graph,
                        spectrometer=spec
                        )

        npos = pc.get_peak_center()
        if npos:
            self.info('new center pos {}'.format(npos))
            if save:
                args = reference_isotope_name, npos
                save = True
                if confirm_save:
                    msg = 'Update Magnet Field Table with new peak center- {} @ {}'.format(*args)
                    save = self.confirmation_dialog(msg)
                if save:
                    spec.magnet.update_field_table(*args)

        elif not self.canceled:
            self.warning_dialog('centering failed')
            self.warning('centering failed')

        #needs to be called on the main thread to properly update
        #the menubar actions. alive=False enables IonOptics>Peak Center
        d = lambda:self.trait_set(alive=False)
        do_later(d)

    def close(self):
        self.alive = False
        self.canceled = True
        self.peak_center.canceled = True
        self.peak_center.stop()
#===============================================================================
# handler
#===============================================================================

    def _graph_factory(self):
        g = Graph(
                  container_dict=dict(padding=5, bgcolor='gray'))
        g.new_plot()
        return g

    def _graph_default(self):
        return self._graph_factory()

#    def graph_view(self):
#        v = View(Item('graph', show_label=False, style='custom'),
#                 width=300,
#                 height=500
#                 )
#        return v
#    def peak_center_view(self):
#        v = View(Item('graph', show_label=False, style='custom'),
#                 width=300,
#                 height=500,
#                 handler=self.handler_klass
#                 )
#        return v

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
