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
from traits.api import Instance, Enum, Any, DelegatesTo, List
from traitsui.api import View, VGroup, HGroup, Group, Item, Spring, spring, Label, \
     ListEditor, InstanceEditor, EnumEditor
from src.managers.manager import Manager
from src.graph.time_series_graph import TimeSeriesStreamGraph
from src.helpers.timer import Timer
import random
#============= standard library imports ========================
#============= local library imports  ==========================
#'black', 'red', 'violet', 'maroon', 'yellow',
from traits.api import HasTraits, Range, Float
from src.spectrometer.detector import Detector
from src.spectrometer.tasks.magnet_scan import MagnetScan
from src.spectrometer.tasks.rise_rate import RiseRate

class Magnet(HasTraits):
    dac = Range(0.0, 6.0)
    def map_mass_to_dac(self, d):
        return d

class Source(HasTraits):
    y_symmetry = Float

class DummySpectrometer(HasTraits):
    detectors = List
    magnet = Instance(Magnet, ())
    source = Instance(Source, ())
    def get_intensities(self):
        return [d.name for d in self.detectors], [random.random() + (i * 12.3) for i in range(len(self.detectors))]

    def get_intensity(self, *args, **kw):
        return 1

class ScanManager(Manager):
    spectrometer = Any

    graph = Instance(TimeSeriesStreamGraph)
    integration_time = Enum(0.065536, 0.131072, 0.262144, 0.524288,
                            1.048576, 2.097152, 4.194304, 8.388608,
                            16.777216, 33.554432, 67.108864)

    detectors = DelegatesTo('spectrometer')
    reference_detector = Instance(Detector)
    magnet = DelegatesTo('spectrometer')
    source = DelegatesTo('spectrometer')
    scanner = Instance(MagnetScan)
    rise_rate = Instance(RiseRate)

    def _graph_changed(self):
        self.rise_rate.graph = self.graph

    def _rise_rate_default(self):
        r = RiseRate(spectrometer=self.spectrometer,
                     graph=self.graph)
        return r

    def _scanner_default(self):
        s = MagnetScan(spectrometer=self.spectrometer)
        return s

    def _reference_detector_changed(self):
        if self.reference_detector:
            self.scanner.reference_detector = self.reference_detector
            self.rise_rate.reference_detector = self.reference_detector

            nominal_width = 1
            emphasize_width = 5
            for name, plot in self.graph.plots[0].plots.iteritems():
                plot = plot[0]
                plot.line_width = emphasize_width if name == self.reference_detector.name else nominal_width

    def _toggle_detector(self, obj, name, old, new):
        self.graph.set_series_visiblity(new, series=obj.name)

    def opened(self):
        self.graph = self._graph_factory()

        self._start_timer()

        #listen to detector for enabling 
        self.on_trait_change(self._toggle_detector, 'detectors.active')

        #force update
        self.reference_detector = None
        #set reference detector default
        self.reference_detector = self.detectors[0]

    def close(self, isok):
        self._stop_timer()

    def _update_scan_graph(self):

        data = self.spectrometer.get_intensities()
        if data:
            _, signals = data
            self.graph.record_multiple(signals, do_later=10)


    def _start_timer(self):
        self._first_iteration = True

        self.info('starting scan timer')
        self.integration_time = 1.048576
        self.timer = self._timer_factory()

    def _stop_timer(self):
        self.info('stopping scan timer')
        self.timer.Stop()

    def _timer_factory(self, func=None):

        if func is None:
            func = self._update_scan_graph

        mult = 1000

        return Timer((self.integration_time + 0.025) * mult, self._update_scan_graph)

    def _graph_factory(self):
        g = TimeSeriesStreamGraph(container_dict=dict(bgcolor='gray',
                                                      padding=5
                                                      )
                                  )
        g.new_plot(padding=[50, 5, 5, 50],
                   xtitle='Time (s)',
                   ytitle='Signal (nA)',
                   )

        for det in self.detectors:
#            if not det.active:
            g.new_series(visible=det.active)
            g.set_series_label(det.name)


#        for det in self.detectors:
#            g.set_series_visiblity(det.active, series=det.name, do_later=10)

        return g

    def _graph_default(self):
        return self._graph_factory()

    def traits_view(self):
#        control_group = VGroup(
##                                HGroup(self._button_factory('defscan', 'defscan_label', None),
#                                       #Item('defscan'),
#
##                                        Item('results'), show_labels=False),
#                                Item('spectrometer', style='custom', show_label=False)
#                                #Item('current_hv', style = 'readonly'),
##                                Item('integration_time'),
##                                Item('molecular_weight', editor = EnumEditor(values = MOLECULAR_WEIGHT_KEYS)),
##                                Item('sub_cup_configuration', show_label = False,
##                                     editor = EnumEditor(values = self.sub_cup_configurations)),
##                                Item('reference_detector', show_label = False, style = 'custom',
##                                                            editor = EnumEditor(
##                                                                               values = self.detector_names,
##                                                                               cols = len(self.detector_names)
##                                                                               )),
##                                Item('active_detectors', show_label = False, style = 'custom',
##                                     editor = CheckListEditor(values = DETECTOR_ORDER,
##                                                              cols = len(DETECTOR_ORDER)
##                                                              )),
#                                #self._slider_factory('magnet_dac', 'magnet_dac'),
#                                #self._slider_factory('magnet_position', 'magnet_position')
#                              )
#        detector_group = Item('detectors',
#                              show_label=False,
#                              editor=TableEditor(columns=[ObjectColumn(name='name', editable=False),
#                                                             ObjectColumn(name='intensity', editable=False),
#                                                             CheckboxColumn(name='active', editable=True),
#                                                             ObjectColumn(name='deflection', editable=True)
#                                                             ],
#                                                    )
#                             )
        custom = lambda n:Item(n, style='custom', show_label=False)
        magnet_grp = VGroup(
                            custom('magnet'),
                            custom('scanner'),
                            label='Magnet'
                            )
        detector_grp = VGroup(
                              Item('reference_detector', editor=EnumEditor(name='detectors')),
                              HGroup(Spring(springy=False, width=100), Label('Deflection')),
                              Item('detectors',
                                   show_label=False,
                                   editor=ListEditor(style='custom', mutable=False, editor=InstanceEditor())),
                              label='Detectors'
                              )

        rise_grp = custom('rise_rate')
        source_grp = custom('source')

        control_grp = Group(
                          source_grp,
                          rise_grp,
                          magnet_grp,
                          detector_grp,
                          layout='tabbed')
        graph_grp = custom('graph')
        v = View(
                    HGroup(
                           control_grp,
                           graph_grp,
                           ),
                    title='Spectrometer Manager',
                    resizable=True,
                    handler=self.handler_klass,
                    width=0.8,
                    height=0.6
                    )
        return v


if __name__ == '__main__':

    detectors = [
             Detector(name='H2',
                      color='black',
                      isheader=True
                      ),
             Detector(name='H1',
                      color='red'
                      ),
             Detector(name='AX',
                      color='violet'
                      ),
             Detector(name='L1',
                      color='maroon'
                      ),
             Detector(name='L2',
                      color='yellow'
                      ),
             Detector(name='CDD',
                      color='lime green',
                      active=False
                      ),

             ]
    sm = ScanManager(
#                     detectors=detectors,
                     spectrometer=DummySpectrometer(detectors=detectors))
#    sm.load_detectors()
    sm.configure_traits()
#============= EOF =============================================
