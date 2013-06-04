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
from traits.api import Range, Instance, Bool, \
     Button, Any, DelegatesTo, Str, Float, Enum
from traitsui.api import View, Item, EnumEditor
from src.managers.manager import Manager
from src.graph.graph import Graph
from src.spectrometer.jobs.peak_center import PeakCenter
# from threading import Thread
from src.spectrometer.detector import Detector
from src.constants import NULL_STR
from src.ui.thread import Thread
from src.ui.gui import invoke_in_main_thread
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

    detectors = DelegatesTo('spectrometer')
    detector = Instance(Detector)
    isotope = Str('Ar40')
    dac = Float

    directions = Enum('Increase', 'Decrease', 'Oscillate')

    def get_mass(self, isotope_key):
        spec = self.spectrometer
        molweights = spec.molecular_weights
        return molweights[isotope_key]

    def position(self, pos, detector, use_dac=False):
        if pos == NULL_STR:
            return

        spec = self.spectrometer
        mag = spec.magnet

        if use_dac:
            dac = pos
        else:
            if isinstance(pos, str):

                # if the pos is an isotope then update the detectors
                spec.update_isotopes(pos, detector)

                # pos is isotope
                pos = self.get_mass(pos)
                mag._mass = pos

            # pos is mass i.e 39.962
            dac = mag.map_mass_to_dac(pos)

        det = spec.get_detector(detector)

        if det:
            dac = spec.correct_dac(det, dac)

            self.info('positioning {} ({}) on {}'.format(pos, dac, detector))
            mag.set_dac(dac)

    def get_center_dac(self, det, iso):
        spec = self.spectrometer
        det = spec.get_detector(det)

        molweights = spec.molecular_weights
        mass = molweights[iso]
        dac = spec.magnet.map_mass_to_dac(mass)

        # correct for deflection
        return spec.correct_dac(det, dac)

#    def _correct_dac(self, det, dac):
#        #        dac is in axial units
#
# #        convert to detector
#        dac *= det.relative_position
#
#        '''
#        convert to axial detector
#        dac_a=  dac_d / relpos
#
#        relpos==dac_detA/dac_axial
#
#        '''
#        #correct for deflection
#        dev = det.get_deflection_correction()
#
#        dac += dev
#
# #        #correct for hv
#        dac *= self.spectrometer.get_hv_correction(current=True)
#        return dac

    def do_peak_center(self, detector=None, isotope=None,
                       period=None,
                       center_dac=None,
                       save=True,
                       confirm_save=False,
                       warn=False,
                       new_thread=True
                       ):
#        spec = self.spectrometer
        if detector is None or isotope is None:
            self.dac = 0
            info = self.edit_traits(view='peak_center_config_view')
            if not info.result:
                return
            else:
                detector = self.detector.name
                isotope = self.isotope
                if self.dac > 0:
                    center_dac = self.dac

        if center_dac is None:
            center_dac = self.get_center_dac(detector, isotope)

        self.canceled = False
        self.alive = True

        if new_thread:
            t = Thread(name='ion_optics.peak_center', target=self._peak_center,
                       args=(detector, isotope, period, center_dac,
                             self.directions,
                             save, confirm_save, warn))
            t.start()
            self._thread = t
            return t
        else:
            self._peak_center(detector, isotope, period, center_dac,
                             self.directions,
                             save, confirm_save, warn)

    def _peak_center(self, detector, isotope, period, center_dac,
                     directions,
                     save, confirm_save, warn):

        self.debug('doing pc')

        spec = self.spectrometer
        self.peak_center = pc = PeakCenter(center_dac=center_dac,
                                           period=period,
                                           directions=directions,
                                           reference_detector=detector,
                                           reference_isotope=isotope,
                                           spectrometer=spec
                                           )

        # bind to the graphs close_func
        # self.close is called when graph window is closed
        # use so we can stop the timer
        pc.graph.close_func = self.close
        # set graph window attributes
        pc.graph.window_title = 'Peak Center {}({}) @ {:0.3f}'.format(detector, isotope, center_dac)

        self.open_view(pc.graph)

        dac_d = pc.get_peak_center()
        self.peak_center_result = dac_d
        if dac_d:
            args = detector, isotope, dac_d
            self.info('new center pos {} ({}) @ {}'.format(*args))

            det = spec.get_detector(detector)

            # correct for hv
            dac_d /= spec.get_hv_correction(current=True)

            # correct for deflection
            dac_d = dac_d - det.get_deflection_correction()

            # convert dac to axial units
            dac_a = dac_d / det.relative_position

            self.info('converted to axial units {}'.format(dac_a))
            args = detector, isotope, dac_a

            if save:
                save = True
                if confirm_save:
                    msg = 'Update Magnet Field Table with new peak center- {} ({}) @ RefDetUnits= {}'.format(*args)
                    save = self.confirmation_dialog(msg)
                if save:
                    spec.magnet.update_field_table(isotope, dac_a)
                    spec.magnet.set_dac(self.peak_center_result)

        elif not self.canceled:
            msg = 'centering failed'
            if warn:
                self.warning_dialog(msg)
            self.warning(msg)

        # needs to be called on the main thread to properly update
        # the menubar actions. alive=False enables IonOptics>Peak Center
#        d = lambda:self.trait_set(alive=False)
        # still necessary with qt? and tasks

        self.trait_set(alive=False)

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
#    def _graph_factory(self):
#        g = Graph(
#                  container_dict=dict(padding=5, bgcolor='gray'))
#        g.new_plot()
#        return g
#
#    def _graph_default(self):
#        return self._graph_factory()

    def _detector_default(self):
        return self.detectors[0]

    def peak_center_config_view(self):
        v = View(Item('detector', editor=EnumEditor(name='detectors')),
               Item('isotope'),
               Item('dac'),
               Item('directions'),
               buttons=['OK', 'Cancel'],
               kind='livemodal',
               title='Peak Center'
               )
        return v
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

#    def traits_view(self):
#        v = View(Item('magnet_dac'),
#                 Item('peak_center_button',
#                      enabled_when='not alive',
#                      show_label=False),
#                 Item('stop_button', enabled_when='alive',
#                       show_label=False),
#
#                 Item('graph', show_label=False, style='custom'),
#
#
#                  resizable=True)
#        return v


if __name__ == '__main__':
    io = IonOpticsManager()
    io.configure_traits()

#============= EOF =============================================
