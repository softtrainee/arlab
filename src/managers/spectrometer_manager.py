'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
from traits.api import Instance, DelegatesTo, Event, Bool, \
 on_trait_change, Any, List, Property, Button
from traitsui.api import View, Item, HGroup, VGroup, TableEditor
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn

#============= standard library imports ========================
import os
from threading import Thread
#============= local library imports  ==========================
from src.managers.manager import Manager
from src.graph.graph import Graph
from src.initializer import Initializer


from src.graph.time_series_graph import TimeSeriesStreamGraph
from src.spectrometer.spectrometer import Spectrometer, DETECTOR_ORDER

class SpectrometerManager(Manager):
    spectrometer = Instance(Spectrometer, ())
    spectrometer_microcontroller = Any
    detectors = DelegatesTo('spectrometer')

    current_hv = DelegatesTo('spectrometer')

    integration_time = DelegatesTo('spectrometer')

    molecular_weight = DelegatesTo('spectrometer')

    test = Button
    #defscan = Button

    defscan = Event
    defscan_label = Property(depends_on='defscanning')
    defscanning = Bool

    results = Button

    scan_graph = Instance(TimeSeriesStreamGraph)
    databuffer = DelegatesTo('spectrometer')

    center_paths = List

    reference_detector = 'H1'
    def set_dac(self, v):
        self.spectrometer.magnet.set_dac(v)

    def get_intensities(self, detector=None, **kw):
        data = self.spectrometer.get_intensities(**kw)
        if detector is not None:
            data = data[DETECTOR_ORDER.index(self.reference_detector)]
        return data

    def get_intensity(self, detector, **kw):
        return self.get_intensities(detector, **kw)

    def load(self):
        self.spectrometer.load()
        return True
#    def opened(self):
#        self.popup = PopupWindow(self.ui.control)

    def finish_loading(self):
        integration_time = 1.048576
        #load the scan graph
        sg = TimeSeriesStreamGraph(container_dict=dict(padding=[5, 5, 5, 30]))
        sg.new_plot(
                    scan_delay=integration_time + 0.025,
                    #data_limit = 15,
                    data_limit=int(300 / integration_time),
                    padding=[30, 0, 0, 0],

                     )
        for _i, _d in enumerate(DETECTOR_ORDER):
            sg.new_series()

        sg.set_series_visiblity(False, series=5)
        sg.plots[0].value_scale = 'log'

        sg.plots[0].underlays.pop(3)
        sg.plots[0].underlays.pop(0)
        self.scan_graph = sg
#        self.spectrometer._timer_factory()

        #set device microcontrollers
        self.spectrometer.set_microcontroller(self.spectrometer_microcontroller)

        #update the current hv
        self.spectrometer.source.read_hv()
        #update the current magnet dac
        self.spectrometer.magnet.read_dac()
        #set integration time
        self.integration_time = integration_time
        #self.integration_time = 0.065536

        self.spectrometer.load_configurations()
        self.spectrometer.finish_loading()

    def deflection_calibration(self):
        #set steering voltage to zero
        self.spectrometer.deflection_calibration()
        self.defscanning = False

    def open_magfield_calibration(self):
        mag = self.spectrometer.magnet
        mag.update_graph()
        mag.graph.edit_traits()

    def peak_center(self, threaded=False, **kw):
        self.spectrometer._alive = True
        func = self.spectrometer.peak_center
        if threaded:
            t = Thread(target=func, kwargs=kw)
            t.start()
        else:
            return func(**kw)

    def _update_hover(self, obj, name, old, new):
        if new is not None:
            g = Graph(container_dict=dict(padding=[30, 0, 0, 30]))
            g.new_plot(padding=5)
            g.new_series()
#            root = os.path.join(data_dir, 'magfield', 'def_calibration001')
            try:
                p = os.path.join(self.results_root, self.center_paths[new])
            except IndexError:
                return
            g.read_xy(p, header=True)

            xs, ys, mx, my = self.spectrometer.calculate_peak_center(g.get_data(), g.get_data(axis=1))
            g.new_series(x=xs, y=ys, type='scatter')
            g.new_series(x=mx, y=my, type='scatter')

            g.window_width = 250
            g.window_height = 250
            g.width = 200
            g.height = 200
            x, y = self.results_graph.current_pos

            g.window_x = x + 75

            g.window_y = 400 - y

            g.edit_traits(kind='popover')

#    def open_calibration_result(self):
#
#
#        root = os.path.join(data_dir, 'magfield')
#        #p = self.open_file_dialog(default_path = root)
#        p = os.path.join(root, 'def_calibration009', 'dac_vs_defl.csv')
#        if p:
#            self.results_root, tail = os.path.split(p)
#            g = ResidualsGraph(
#                               container_dict = dict(padding = [20, 5, 15, 15],
#                                                     ),
#                                window_height = 700,
#
#                               )
#            g.on_trait_change(self._update_hover, 'hover_index')
#            g.new_plot(
#                       padding_top = 15,
#                       padding_right = 15,
#                       xtitle = 'Deflection (V)',
#                       ytitle = '40Ar Peak Center (Magnet DAC V)'
#                       #padding = [30, 1, 1, 30]
#                       )
##            p = os.path.join(root, 'dac_vs_defl.csv')
#    #        g.read_xy(p, header = True)
#            x = []
#            y = []
#            reader = csv.reader(open(p, 'r'))
#            reader.next()
#            for line in reader:
#                if len(line) != 2:
#                    break
#                x.append(float(line[0]))
#                y.append(float(line[1]))
#            g.new_series(x = x, y = y)
#
#            for p in os.listdir(self.results_root):
#                if p.startswith('peak_scan'):
#                    self.center_paths.append(p)
#                #self.centering_paths
#
#
#            self.results_graph = g
#            g.edit_traits()
#===============================================================================
# property get/set
#===============================================================================

#===============================================================================
# change handlers
#===============================================================================
    def _test_fired(self):
        pass
#        self.open_magfield_calibration()

    def _defscan_fired(self):
        if self.spectrometer.stop():
            self.defscanning = True
            t = Thread(target=self.deflection_calibration)
            t.start()
        else:
            self.defscanning = False

    def _results_fired(self):
        self.open_calibration_result()

    @on_trait_change('databuffer')
    def _update_scan_graph(self, obj, name, old, new):
        ys = [float(yi) for yi in new.split(',')]
        self.scan_graph.record_multiple(ys)

#    def _integration_time_changed(self):
#        self.spectrometer_microcontroller.ask('SetIntegrationTime {}'.format(self.integration_time))
#        self.scan_graph.set_scan_delay(self.integration_time + 0.025)
#        self.spectrometer.reset_scan_timer()

#    def _molecular_weight_changed(self):
#        self._set_magnet_position(MOLECULAR_WEIGHTS[self.molecular_weight])

    @on_trait_change('detectors:active')
    def _active_detectors_changed(self, obj, name, old, new):
        self.scan_graph.set_series_visiblity(new, series=DETECTOR_ORDER.index(obj.name))

    def _get_defscan_label(self):
        return 'Start' if not self.defscanning else 'Stop'

    def traits_view(self):
        control_group = VGroup(
                                HGroup(self._button_factory('defscan', 'defscan_label', None),
                                       #Item('defscan'),

                                        Item('results'), show_labels=False),
                                Item('spectrometer', style='custom', show_label=False)
                                #Item('current_hv', style = 'readonly'),
#                                Item('integration_time'),
#                                Item('molecular_weight', editor = EnumEditor(values = MOLECULAR_WEIGHT_KEYS)),
#                                Item('sub_cup_configuration', show_label = False,
#                                     editor = EnumEditor(values = self.sub_cup_configurations)),
#                                Item('reference_detector', show_label = False, style = 'custom',
#                                                            editor = EnumEditor(
#                                                                               values = self.detector_names,
#                                                                               cols = len(self.detector_names)
#                                                                               )),
#                                Item('active_detectors', show_label = False, style = 'custom',
#                                     editor = CheckListEditor(values = DETECTOR_ORDER,
#                                                              cols = len(DETECTOR_ORDER)
#                                                              )),
                                #self._slider_factory('magnet_dac', 'magnet_dac'),
                                #self._slider_factory('magnet_position', 'magnet_position')
                              )
        graph_group = Item('scan_graph', show_label=False, style='custom')
        detector_group = Item('detectors',
                              show_label=False,
                              editor=TableEditor(columns=[ObjectColumn(name='name', editable=False),
                                                             ObjectColumn(name='intensity', editable=False),
                                                             CheckboxColumn(name='active', editable=True),
                                                             ObjectColumn(name='deflection', editable=True)
                                                             ],



                                                    )
                              )
        return View(
                    HGroup(
                           detector_group,
                           control_group,
                           graph_group,

                           ),
                    title='Spectrometer Manager',
                    resizable=True,
                    handler=self.handler_klass
                    )
if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('spectrometer')
    s = SpectrometerManager()
    ini = Initializer()
    ini.add_initialization(dict(name='spectrometer_manager',
                                manager=s
                                ))
    ini.run()
#    s.magnet_field_calibration()
    s.configure_traits()#kind = 'live')
#============= EOF =============================================
