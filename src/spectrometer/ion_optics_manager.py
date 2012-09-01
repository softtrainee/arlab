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
from src.spectrometer.molecular_weights import MOLECULAR_WEIGHTS
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

    peak_center_result = None

    def get_hv_correction(self, current=False):
        source = self.spectrometer.source
        cur = source.current_hv
        if current:
            cur = source.read_hv()

        if cur is None:
            cor = 1
        else:
            cor = source.nominal_hv / cur
        return cor

    def position(self, pos, detector, use_dac):
        spec = self.spectrometer
        mag = spec.magnet

        if use_dac:
            dac = pos
        else:
            if isinstance(pos, str):
                #pos is in isotope
                pos = MOLECULAR_WEIGHTS[pos]

                #if the pos is an isotope then updated the detectors
                spec.update_isotopes(detector, pos)

            #pos is mass i.e 39.962
            dac = mag.map_mass_to_dac(pos)

        det = spec.get_detector(detector)

        '''
        convert to axial detector 
        dac_a=  dac_s / relpos
        
        relpos==dac_detA/dac_axial 
        
        '''
        dac /= det.relative_position

        #correct for deflection
        dev = det.get_deflection_correction()
        dac += dev

#        #correct for hv
        dac *= self.get_hv_correction(current=True)
        mag.set_dac(dac)

    def do_peak_center(self, detector='H1', isotope='Ar40', save=True, confirm_save=False):
        spec = self.spectrometer

        self.canceled = False
        self.alive = True

        t = Thread(name='ion_optics.peak_center', target=self._peak_center,
                   args=(detector, isotope, spec.magnet.dac, save, confirm_save))
        t.start()
        return t

    def _peak_center(self, detector, isotope, center_dac, save, confirm_save):
        graph = self._graph_factory()

        #set graph window attributes
        graph.window_title = 'Peak Center {}({}) @ {:0.3f}'.format(detector, isotope, center_dac)

        #bind to the graphs close_func
        #self.close is called when graph window is closed
        #use so we can stop the timer
        graph.close_func = self.close

        self.open_view(graph)

#        reference_detector_name = 'AX'
#        reference_isotope_name = 'Ar40'
        spec = self.spectrometer

        self.peak_center = pc = PeakCenter(center_dac=center_dac,
                        reference_isotope=isotope,
                        graph=graph,
                        spectrometer=spec
                        )

        npos = pc.get_peak_center()
        self.peak_center_result = npos
        if npos:
            args = detector, isotope, npos
            self.info('new center pos {} ({}) @ {}'.format(*args))

            det = spec.get_detector(detector)
            npos /= det.relative_position

            self.info('converted to axial units {}'.format(npos))
            args = detector, isotope, npos

            if save:
                save = True
                if confirm_save:
                    msg = 'Update Magnet Field Table with new peak center- {} ({}) @ {}'.format(*args)
                    save = self.confirmation_dialog(msg)
                if save:
                    spec.magnet.update_field_table(isotope, npos)

        elif not self.canceled:
            self.warning_dialog('centering failed')
            self.warning('centering failed')

        #needs to be called on the main thread to properly update
        #the menubar actions. alive=False enables IonOptics>Peak Center
        d = lambda:self.trait_set(alive=False)
        do_later(d)

    def close(self):
        self.cancel_peak_center()

    def cancel_peak_center(self):
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
