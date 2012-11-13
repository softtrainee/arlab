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
from src.canvas.popup_window import PopupWindow
from src.graph.context_menu_mixin import IsotopeContextMenuMixin
from src.graph.stacked_graph import StackedGraph
from chaco.data_label import DataLabel
from chaco.tools.data_label_tool import DataLabelTool

class mStackedGraph(StackedGraph, IsotopeContextMenuMixin):
    def set_status(self):
        self.plotter.set_status()

    def recall_analysis(self):
        self.plotter.recall_analysis()

class Plotter(Viewable):
    adapter = Property
    results = List(BaseResults)
    graph = Any
    db = Any
    selected_analysis = Any
    analyses = Any
    sorted_analyses = Property(depends_on='analyses')
    error_bar_overlay = Any
    figure = Any
    popup = None
    _dehover_count = 0
    _hover_cache = None
#    hoverid = None
    def recall_analysis(self):
        self.popup.Close()
        dbrecord = self.selected_analysis.dbrecord

        from src.database.orms.isotope_orm import meas_AnalysisTable
        sess = self.db.new_session()
        self.db.sess = sess
        q = sess.query(meas_AnalysisTable)
        q = q.filter(meas_AnalysisTable.id == dbrecord._dbrecord.id)
        dbr = q.one()
#        print id(dbr), dbr
        dbrecord._dbrecord = dbr

        dbrecord.load_graph()
        dbrecord.edit_traits()

#        sess.close()
#        sess.remove()
#        self.selected_analysis.dbrecord.edit_traits()

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

    def _add_scatter_inspector(self, container, plot, scatter, group_id=0, add_tool=True, popup=True):
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
        if add_tool:
            rect_tool = RectSelectionTool(scatter,
    #                                      parent=self,
                                          container=container,
                                          plot=plot,
                                          group_id=group_id
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
#        if popup:
            u = lambda a, b, c, d: self.update_graph_metadata(group_id, a, b, c, d)
            scatter.index.on_trait_change(u, 'metadata_changed')


#        self.metadata = scatter.index.metadata
    def _add_data_label(self, s, text, point, **kw):
        label = DataLabel(component=s, data_point=point,
                          label_position='top right',
                          label_text=text,
                          border_visible=False,
                          bgcolor='transparent',
                          show_label_coords=False,
                          marker_visible=False,
                          text_color=s.color,
                          arrow_color=s.color,
                          **kw
                          )
        s.overlays.append(label)
        tool = DataLabelTool(label)
        label.tools.append(tool)
        return label

    def _get_sorted_analyses(self):
        return sorted([a for a in self.analyses], key=self._cmp_analyses)

    def get_labnumber(self, analyses):
        return ', '.join(sorted(list(set(['{}-{}'.format(a.labnumber, a.aliquot) for a in analyses]))))

    def update_graph_metadata(self, group_id, obj, name, old, new):
        sorted_ans = [a for a in self.sorted_analyses if a.group_id == group_id]

        hover = obj.metadata.get('hover')
        if hover:
#            print hover, group_id
            hoverid = hover[0]
#            self.hoverid = hoverid
#            try:
#                self._hover_cache[group_id] = hoverid
#            except:
#                self._hover_cache = {group_id:hoverid}

            try:
                self.selected_analysis = sa = sorted_ans[hoverid]
            except IndexError:
                return

            if not self.popup:
                self.popup = PopupWindow(None)

#            print event.x, event.y
            self._show_pop_up(self.popup, sa, obj)
        else:
#            if self._dehover_count >= len(self._hover_cache.keys()):
#                self._dehover_count = 0
#            elif len(self._hover_cache.keys()):
#                self._dehover_count += 1
#                return

            if self.popup:
#                self.popup.Freeze()
                self.popup.Show(False)
#                self.popup.Thaw()
                self.popup.Destroy()

        sel = obj.metadata.get('selections', [])
        #set the temp_status for all the analyses
        for i, a in enumerate(sorted_ans):
            a.temp_status = -1 if i in sel else 1

    def _cmp_analyses(self, x):
        return x.timestamp

    def _show_pop_up(self, popup, analysis, obj):
        try:
            x, y = obj.metadata.get('mouse_xy')
        except Exception, e:
#            popup.Show(False)
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
#        popup.Freeze()
        popup.SetPosition((x + 55, y + 25))
        popup.set_size(ml, mh)
        popup.SetText(t)
        popup.Show(True)
#        popup.Thaw()

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
