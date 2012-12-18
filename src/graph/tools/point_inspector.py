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
from traits.api import HasTraits, Instance, Event, on_trait_change, Callable
from traitsui.api import View, Item, TableEditor
from chaco.abstract_overlay import AbstractOverlay
from enable.base_tool import BaseTool
from src.graph.tools.info_inspector import InfoInspector, InfoOverlay
#============= standard library imports ========================
#============= local library imports  ==========================
class PointInspector(InfoInspector):
    convert_index = Callable
#    def _build_metadata(self, xy):
#        point = self.component.hittest(xy)
#        md = dict(point=point)
#        return md
    def assemble_lines(self):
        pt = self.current_position
        if pt:
            x, y = self.component.map_data(pt)
            if self.convert_index:
                x = self.convert_index(x)
            return ['{},{}'.format(x, y)]
        else:
            return []

class PointInspectorOverlay(InfoOverlay):
    pass
#            print comp
#============= EOF =============================================
