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
from traits.api import HasTraits, Property, Unicode, List, \
    Instance, Float, Int, Bool, Event, DelegatesTo, Any
from traitsui.api import View, Item, UItem, VGroup, ButtonEditor
from src.envisage.tasks.base_editor import BaseTraitsEditor
from src.loggable import Loggable
from src.canvas.canvas2D.raster_canvas import RasterCanvas
from enable.component_editor import ComponentEditor
from src.lasers.power.power_mapper import PowerMapper
from src.ui.thread import Thread
from src.lasers.power.power_map_processor import PowerMapProcessor
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.graph.graph import Graph
from src.graph.contour_graph import ContourGraph
from chaco.plot_containers import HPlotContainer
from src.lasers.tasks.editors.laser_editor import LaserEditor
#============= standard library imports ========================
#============= local library imports  ==========================


class PowerMapControls(HasTraits):
    beam_diameter = Float(1)
    request_power = Float(1)
    padding = Float(1.0)
    step_length = Float(0.25)
    center_x = Float(0)
    center_y = Float(0)
    integration = Int(1)
    discrete_scan = Bool(False)

    def traits_view(self):
        v = View(VGroup(

                        Item('discrete_scan'),
                        Item('beam_diameter'),
                        Item('request_power'),
                        Item('padding'),
                        Item('step_length'),
                        Item('center_x'),
                        Item('center_y'),

                    )
                 )
        return v

class PowerMapEditor(LaserEditor):

    canvas = Instance(RasterCanvas, ())
    editor = Instance(PowerMapControls, ())
    mapper = Instance(PowerMapper, ())
    completed = DelegatesTo('mapper')
    was_executed = False

    def load(self, path):

        pmp = PowerMapProcessor()

        reader = H5DataManager()
        reader.open_data(path)
        cg = pmp.load_graph(reader)

        self.component = cg.plotcontainer
        self.was_executed = True

#     def do_execute(self, lm):
    def _do_execute(self):
        mapper = self.mapper
        mapper.laser_manager = self._laser_manager

        editor = self.editor
        padding = editor.padding

        if editor.discrete_scan:
            mapper.canvas = self.canvas
            self.component = self.canvas
        else:

            c = mapper.make_component(padding)
            self.component = c

        bd = editor.beam_diameter
        rp = editor.request_power
        cx = editor.center_x
        cy = editor.center_y
        step_len = editor.step_length

#         mapper.do_power_mapping(bd, rp, cx, cy, padding, step_len)
        t = Thread(target=mapper.do_power_mapping,
                   args=(bd, rp, cx, cy, padding, step_len))
        t.start()
        self._execute_thread = t

        return True

    def stop(self):
        self.mapper.stop()

    def traits_view(self):
        v = View(
                 UItem('component', editor=ComponentEditor())
                 )
        return v

#============= EOF =============================================
