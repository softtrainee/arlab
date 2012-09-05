#===============================================================================
# Copyright 2011 Jake Ross
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
from traits.api import Instance, DelegatesTo, Event, Bool, \
 on_trait_change, Any, List, Property, Button
#from traitsui.api import View, Item, HGroup, VGroup, TableEditor
#from traitsui.table_column import ObjectColumn
#from traitsui.extras.checkbox_column import CheckboxColumn

#============= standard library imports ========================
#import os
#from threading import Thread
#============= local library imports  ==========================
from src.managers.manager import Manager
#from src.graph.graph import Graph
#from src.initializer import Initializer


#from src.graph.time_series_graph import TimeSeriesStreamGraph
from src.spectrometer.spectrometer import Spectrometer
import os
from src.paths import paths
from src.spectrometer.tasks.relative_detector_positions import RelativeDetectorPositions
#from src.spectrometer.ion_optics_manager import IonOpticsManager
#from src.spectrometer.scan_manager import ScanManager

class SpectrometerManager(Manager):
    spectrometer = Instance(Spectrometer, ())
    spectrometer_microcontroller = Any

    def load(self):


        self.spectrometer.load()

        config = self.get_configuration(path=os.path.join(paths.spectrometer_dir, 'detectors.cfg'))
        for name in config.sections():
            relative_position = self.config_get(config, name, 'relative_position', cast='float')
            color = self.config_get(config, name, 'color', default='black')
            default_state = self.config_get(config, name, 'default_state', default=True, cast='boolean')
            isotope = self.config_get(config, name, 'isotope')
            self.spectrometer.add_detector(name=name,
                                            relative_position=relative_position,
                                            color=color,
                                            active=default_state,
                                            isotope=isotope
                                            )


        return True
##    def opened(self):
##        self.popup = PopupWindow(self.ui.control)
#
    def finish_loading(self):
        integration_time = 1.048576

        #set device microcontrollers
        self.spectrometer.set_microcontroller(self.spectrometer_microcontroller)

        #update the current hv
        self.spectrometer.source.sync_parameters()
        #update the current magnet dac
        self.spectrometer.magnet.read_dac()
        #set integration time
        self.integration_time = integration_time
        #self.integration_time = 0.065536

        self.spectrometer.load_configurations()
        self.spectrometer.finish_loading()

#    def calculate_relative_detector_positions(self):
#        # set all deflections to 0
#
#        ion = self.application.get_service('src.spectrometer.ion_optics_manager.IonOpticsManager')
#
#        #peak center on the axial detector
#        t = ion.do_peak_center('AX', 'Ar36', save=False)
#        t.join()
#
#        axial_dac = ion.peak_center_result
#        #peak center on all detectors
#        for d in self.spectrometer.detectors:
#            if not self.isAlive():
#                break
#            if d.name is not 'AX':
#                t = ion.do_peak_center(d.name, 'Ar36', save=False)
#                t.join()
#            rp = ion.peak_center_result / axial_dac
#            self.info('calculated relative position {} to AX = {}'.format(d.name, rp))

    def relative_detector_positions_task_factory(self):
        ion = self.application.get_service('src.spectrometer.ion_optics_manager.IonOpticsManager')
        return RelativeDetectorPositions(spectrometer=self.spectrometer,
                                         ion_optics_manager=ion
                                         )


#    def deflection_calibration(self):
#        #set steering voltage to zero
#        self.spectrometer.deflection_calibration()
#        self.defscanning = False
#
#    def open_magfield_calibration(self):
#        mag = self.spectrometer.magnet
#        mag.update_graph()
#        mag.graph.edit_traits()
#
#===============================================================================
# property get/set
#===============================================================================

#===============================================================================
# change handlers
#===============================================================================

##===============================================================================
## property getter/setters
##===============================================================================
#    def _get_defscan_label(self):
#        return 'Start' if not self.defscanning else 'Stop'

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup
    logging_setup('spectrometer')
##    s = SpectrometerManager()
#    ini = Initializer()
#    ini.add_initialization(dict(name='spectrometer_manager',
#                                manager=s
#                                ))
#    ini.run()
##    s.magnet_field_calibration()
#    s.configure_traits()#kind = 'live')
#============= EOF =============================================
#    def _update_hover(self, obj, name, old, new):
#        if new is not None:
#            g = Graph(container_dict=dict(padding=[30, 0, 0, 30]))
#            g.new_plot(padding=5)
#            g.new_series()
##            root = os.path.join(data_dir, 'magfield', 'def_calibration001')
#            try:
#                p = os.path.join(self.results_root, self.center_paths[new])
#            except IndexError:
#                return
#            g.read_xy(p, header=True)
#
#            xs, ys, mx, my = self.spectrometer.calculate_peak_center(g.get_data(), g.get_data(axis=1))
#            g.new_series(x=xs, y=ys, type='scatter')
#            g.new_series(x=mx, y=my, type='scatter')
#
#            g.window_width = 250
#            g.window_height = 250
#            g.width = 200
#            g.height = 200
#            x, y = self.results_graph.current_pos
#
#            g.window_x = x + 75
#
#            g.window_y = 400 - y
#
#            g.edit_traits(kind='popover')
#
