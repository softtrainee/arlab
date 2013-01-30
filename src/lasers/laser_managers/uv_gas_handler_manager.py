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
from traits.api import HasTraits, Instance, Any, Button
from traitsui.api import View, Item, TableEditor, HGroup
from src.viewable import Viewable
from enable.component_editor import ComponentEditor
from src.canvas.canvas2D.extraction_line_canvas2D import ExtractionLineCanvas2D
import os
from src.paths import paths
#from src.managers.manager import Manager
from src.extraction_line.valve_manager import ValveManager
#============= standard library imports ========================
#============= local library imports  ==========================

class UVGasHandlerManager(ValveManager):
    canvas = Instance(ExtractionLineCanvas2D)
    controller = Any
    use_explanation = False
    mode = 'normal'

    auto_gas_exchange = Button

    def set_software_lock(self, name, lock):
        if lock:
            self.lock(name)
        else:
            self.unlock(name)

    def load(self):
        path = os.path.join(paths.extraction_line_dir, 'uv_gas_handling_valves.xml')
        self._load_valves_from_file(path)
        return True

    def open_valve(self, name, mode):
        pass
#        v = self.get_valve_by_name(name)
#        self.controller.open_valve(v.address)
#        return True

    def close_valve(self, name, mode):
        pass
#        v = self.get_valve_by_name(name)
#        self.controller.close_valve(v.address)
#        return True

    def set_selected_explanation_item(self, item):
        pass

    def _auto_gas_exchange(self):
        self.info('Starting auto gas exchange')
        self.controller.start_auto_gas_exchange()
#===============================================================================
# handlers
#===============================================================================
    def _auto_gas_exchange_fired(self):
        self._auto_gas_exchange()

    def _canvas_default(self):
        p = os.path.join(paths.canvas2D_dir, 'uv_gas_handling_canvas.xml')
        canvas = ExtractionLineCanvas2D(manager=self)
        canvas.load_canvas_file(p)
        return canvas

    def traits_view(self):
        ctrl_grp = HGroup(Item('auto_gas_exchange', show_label=False))
        v = View(
                 ctrl_grp,
                 Item('canvas',
                      show_label=False,
                      editor=ComponentEditor(),
                      ), resizable=True,
                 width=700,
                 height=500
                 )
        return v
#============= EOF =============================================
