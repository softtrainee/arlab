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
from traits.api import Property, List, Any
from traitsui.api import View, Item, VGroup, TabularEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.viewable import Viewable
from src.processing.plotters.results_tabular_adapter import ResultsTabularAdapter, \
    BaseResults
from chaco.tools.scatter_inspector import ScatterInspector
from chaco.scatter_inspector_overlay import ScatterInspectorOverlay

class Plotter(Viewable):
    adapter = Property
    results = List(BaseResults)
    graph = Any
    selected_analysis = Any
    analyses = Any

    def _get_adapter(self):
        return ResultsTabularAdapter

    def _get_content(self):
        return

    def _add_scatter_inspector(self, scatter, gid=0):
        #add a scatter hover tool
        scatter.tools.append(ScatterInspector(scatter, selection_mode='off'))
        overlay = ScatterInspectorOverlay(scatter,
                    hover_color="red",
                    hover_marker_size=6,
                    )
        scatter.overlays.append(overlay)
        u = lambda a, b, c, d: self.update_graph_metadata(gid, a, b, c, d)
        scatter.index.on_trait_change(u, 'metadata_changed')
#        self.metadata = scatter.index.metadata

    def update_graph_metadata(self, gid, obj, name, old, new):
#        print gid, obj, name, old, new
        hover = obj.metadata.get('hover')
        if hover:
            hoverid = hover[0]
            self.selected_analysis = sorted([a for a in self.analyses if a.gid == gid], key=self._cmp_analyses)[hoverid]

#        hover = self.metadata.get('hover')
#        if hover:
#            hoverid = hover[0]
#            self.selected_analysis = sorted([a for a in self.analyses ], key=self._cmp_analyses)[hoverid]

    def _cmp_analyses(self, x):
        return x.timestamp
#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        results = Item('results',
                      style='custom',
                      show_label=False,
                      editor=TabularEditor(adapter=self.adapter()))
        ct = self._get_content()

        vg = VGroup(ct, results) if ct is not None else VGroup(results)
        v = View(vg)
        return v
#============= EOF =============================================
