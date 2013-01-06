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
from traits.api import Instance, Int, Float, Either, Any, Str
from traitsui.api import View, Item
from enable.component_editor import ComponentEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.graph.graph_container import HGraphContainer
from src.viewable import Viewable

class Window(Viewable):
    container = Instance(HGraphContainer, ())
    window_width = Either(Int, Float)
    window_height = Either(Int, Float)
    window_x = Either(Int, Float)
    window_y = Either(Int, Float)

    open_event = Any
    title = Str('  ')

    def traits_view(self):
        v = View(Item('container',
                         show_label=False, style='custom',
                         editor=ComponentEditor(),
                         ),
                 handler=self.handler_klass,
                 resizable=True,
                 width=self.window_width,
                 height=self.window_height,
                 x=self.window_x,
                 y=self.window_y,
                 title=self.title
                 )
        return v
#============= EOF =============================================
