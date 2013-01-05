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
from traits.api import HasTraits, List, Callable
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
from numpy import where
from src.graph.tools.point_inspector import PointInspector
#============= local library imports  ==========================
class AnalysisPointInspector(PointInspector):
    analyses = List
    value_format = Callable


    def assemble_lines(self):
        lines = []
        if self.current_position:
            ind = self.get_selected_index()
            if ind is not None:
                ind = ind[0]
                analysis = self.analyses[ind]
                rid = analysis.record_id
                name = self.component.container.y_axis.title

                y = self.component.value.get_data()[ind]
                if self.value_format:
                    y = self.value_format(y)

                if analysis.temp_status != 0:
                    status = 'Temp. Omitted'
                else:
                    status = analysis.status_text

                lines = ['Analysis= {}'.format(rid),
                         'Status= {}'.format(status),
                         '{}= {}'.format(name, y)
                         ]
        return lines

#============= EOF =============================================