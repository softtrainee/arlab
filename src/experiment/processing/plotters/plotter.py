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
from traits.api import Property, List, Any, Range
from traitsui.api import View, Item, VGroup, TabularEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.viewable import Viewable
from src.experiment.processing.plotters.results_tabular_adapter import ResultsTabularAdapter, \
    BaseResults
from chaco.tools.scatter_inspector import ScatterInspector
from chaco.scatter_inspector_overlay import ScatterInspectorOverlay
from chaco.array_data_source import ArrayDataSource
from src.graph.error_bar_overlay import ErrorBarOverlay
from src.graph.tools.rect_selection_tool import RectSelectionTool, \
    RectSelectionOverlay
from chaco.tools.broadcaster import BroadcasterTool
from enable.font_metrics_provider import font_metrics_provider

class Plotter(Viewable):
    adapter = Property
    results = List(BaseResults)
    graph = Any
    selected_analysis = Any
    analyses = Any
    error_bar_overlay = Any
    figure = Any
    popup = None
    def _get_adapter(self):
        return ResultsTabularAdapter

    def _get_toolbar(self):
        return

    def _get_content(self):
        content = Item('results',
                      style='custom',
                      show_label=False,
                      editor=TabularEditor(adapter=self.adapter(),
                                           auto_update=True
                                           ),
                       height=50
                       )
        return content

    def _add_error_bars(self, scatter, errors, axis, sigma_trait=None):
        ebo = ErrorBarOverlay(component=scatter, orientation=axis)
        scatter.underlays.append(ebo)
        setattr(scatter, '{}error'.format(axis), ArrayDataSource(errors))
        if sigma_trait:
            self.on_trait_change(ebo.update_sigma, sigma_trait)

    def _add_scatter_inspector(self, container, plot, scatter, group_id=0, popup=True):
        #add a scatter hover tool
#        bc = BroadcasterTool()
#        broadcaster = BroadcasterTool()
#        scatter.tools.append(broadcaster)
#        self.plots[plotid].container.tools.append(broadcaster)
#        scatter.tools.append(ScatterInspector(scatter,
##                                              selection_mode='off'
#                                              ))

#        broadcaster.tools.append(ScatterInspector(scatter,
##                                              selection_mode='off'
#                                              ))

#        rect_tool = RectSelectionTool(scatter,
##                                      parent=self,
##                                      plot=self.graph.plots[0],
#                                      plotid=1
#                                      )

        rect_tool = RectSelectionTool(scatter,
#                                      parent=self,
                                      container=container,
                                      plot=plot,
#                                      plotid=1
                                      )
        rect_overlay = RectSelectionOverlay(
                                            tool=rect_tool)

#        broadcaster.tools.append(rect_tool)
        scatter.tools.append(rect_tool)
        scatter.overlays.append(rect_overlay)


#        scatter.overlays.append(rect_tool)
#        overlay = ScatterInspectorOverlay(scatter,
#                    hover_color="red",
#                    hover_marker_size=int(scatter.marker_size + 2),
                    #selection_color='transparent',
                    #selection_marker_size=int(scatter.marker_size),
                    #selection_marker=scatter.marker
#                    selection_outlin
#                    )
#        scatter.overlays.append(overlay)
        if popup:
            u = lambda a, b, c, d: self.update_graph_metadata(group_id, a, b, c, d)
            scatter.index.on_trait_change(u, 'metadata_changed')
#        self.metadata = scatter.index.metadata

    def update_graph_metadata(self, group_id, obj, name, old, new):
        pass
#        print group_id, obj, name, old, new
        hover = obj.metadata.get('hover')
#        print hover
        if hover:
#            print hover, group_id
            hoverid = hover[0]
#            for ai in self.analyses:
#                print ai.group_id
            self.selected_analysis = sa = sorted([a for a in self.analyses if a.group_id == group_id], key=self._cmp_analyses)[hoverid]
            event = obj.metadata.get('mouse_xy')
            from src.canvas.popup_window import PopupWindow
            if not self.popup:
                self.popup = PopupWindow(None)

#            print event.x, event.y
            self._show_pop_up(self.popup, sa, event)
        else:
            if self.popup:
                self.popup.Show(False)



#        print hover
#        hover = self.metadata.get('hover')
#        if hover:
#            hoverid = hover[0]

#            self.selected_analysis = sorted([a for a in self.analyses ], key=self._cmp_analyses)[hoverid]

    def _cmp_analyses(self, x):
        return x.timestamp

    def _show_pop_up(self, popup, analysis, mouse_xy):
        try:
            x, y = mouse_xy
        except:
            return

        lines = [
                 analysis.rid,
                 analysis.age_string
               ]
        t = '\n'.join(lines)
        gc = font_metrics_provider()
        with gc:
            font = popup.GetFont()
            from kiva.fonttools import Font
            gc.set_font(Font(face_name=font.GetFaceName(),
                             size=font.GetPointSize(),
                             family=font.GetFamily(),
#                             weight=font.GetWeight(),
#                             style=font.GetStyle(),
#                             underline=0, 
#                             encoding=DEFAULT
                             ))
            linewidths, lineheights = zip(*[gc.get_full_text_extent(line)[:2]  for line in lines])
#            print linewidths, lineheights
            ml = max(linewidths)
            mh = max(lineheights)

#        ch = popup.GetCharWidth()
        mh = mh * len(lines)
#        print ml, mh
        popup.Freeze()
        popup.set_size(ml, mh)
        popup.SetText(t)
        popup.SetPosition((x + 55, y + 25))
        popup.Show(True)
        popup.Thaw()

#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        content = self._get_content()
        tb = self._get_toolbar()

        vg = VGroup(tb, content) if tb is not None else VGroup(content)
        v = View(vg)
        return v
#============= EOF =============================================
