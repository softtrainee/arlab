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
from traits.api import Property, List, Any, Range, Dict, Instance
from traitsui.api import View, Item, VGroup, TabularEditor
#============= standard library imports ========================
from numpy import linspace
#============= local library imports  ==========================
from src.viewable import Viewable
from src.processing.plotters.results_tabular_adapter import ResultsTabularAdapter, \
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
from sqlalchemy.orm.session import object_session
from chaco.plot_containers import GridPlotContainer
from src.processing.plotters.graph_panel_info import GraphPanelInfo

class mStackedGraph(StackedGraph, IsotopeContextMenuMixin):
    plotter = Any
    selected_analysis = Property(
#                                 depends_on='plotter'
                                 )
    def close_popup(self):
        popup = self.plotter.popup
        if popup:
            popup.Close()

    def _get_selected_analysis(self):

        if self.plotter:
            if self.plotter.selected_analysis:
                if hasattr(self.plotter.selected_analysis, 'dbrecord'):
                    return self.plotter.selected_analysis
#                if self.plotter.selected_analysis.dbrecord:
#                    return self.plotter.selected_analysis
    def set_status_omit(self):
        self.plotter.set_status(1)

    def set_status_include(self):
        self.plotter.set_status(0)

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
    _hover_cache = Dict

    graph_panel_info = Instance(GraphPanelInfo, ())

#    hoverid = None

    def build(self, analyses=None, padding=None,
              options=None
              ):

        if analyses is None:
            analyses = self.analyses

        if options is None:
            options = self.options

        self.options = options
        self.analyses = analyses
        graph_ids = sorted(list(set([a.graph_id for a in analyses])))
        def get_analyses(gii):
            return [a for a in analyses if a.graph_id == gii]

        graph_groups = [get_analyses(gi)
                            for gi in graph_ids]
        self._ngroups = n = len(graph_groups)

        op, r, c = self._create_grid_container(n)
        self._plotcontainer = op
        self.graphs = []
        self.results = []
        plots = []

        aux_plots = self._get_plot_option(options, 'aux_plots', default=[])
        title = self._get_plot_option(options, 'title')
        xtick_font = self._get_plot_option(options, 'xtick_font', default='modern 10')
        xtitle_font = self._get_plot_option(options, 'xtitle_font', default='modern 12')
        ytick_font = self._get_plot_option(options, 'ytick_font', default='modern 10')
        ytitle_font = self._get_plot_option(options, 'ytitle_font', default='modern 12')
        for i in range(r):
            for j in range(c):
                k = i * c + j
                try:
                    ans = graph_groups[k]
                except IndexError:
                    break

                g = self._build(ans, padding=padding,
                                aux_plots=aux_plots,
                                title=self._make_title(ans) if title is None else title
                                )
                if i == r - 1:
                    self._build_xtitle(g, xtitle_font, xtick_font)

                if j == 0:
                    self._build_ytitle(g, ytitle_font, ytick_font, aux_plots)

                for pi in g.plots:
                    pi.y_axis.tick_in = False

                op.add(g.plotcontainer)
                self.graphs.append(g)
                for pi in g.plots:
                    plots.append(pi)

        self._plots = plots
        return op, plots

    def _build_xtitle(self, *args, **kw):
        pass
    def _build_ytitle(self, *args, **kw):
        pass

    def _build(self, analyses, aux_plots=None, padding=None, title=''):
        if aux_plots is None:
            aux_plots = []

        if padding is None:
            padding = [50, 5 , 35, 35]


        g = mStackedGraph(panel_height=200,
                            equi_stack=False,
                            container_dict=dict(padding=0),
                            plotter=self
                            )
        g.clear()
#        g.plotcontainer.tools.append(TraitsTool(g.plotcontainer))
        g._has_title = True

        p = g.new_plot(padding=padding, title=None if aux_plots else title)
        p.value_range.tight_bounds = False

        for i, ap in enumerate(aux_plots):
            kwargs = dict(padding=padding,
                       bounds=[50, ap['height']])

            if i == len(aux_plots) - 1:
                kwargs['title'] = title

            p = g.new_plot(**kwargs)
            if ap['scale'] == 'log':
                p.value_range.tight_bounds = True
            else:
                p.value_range.tight_bounds = False

        g.set_grid_traits(visible=False)
        g.set_grid_traits(visible=False, grid='y')
        self._build_hook(g, analyses, padding, aux_plots=aux_plots)
        return g

    def recall_analysis(self):
        if self.popup:
            self.popup.Close()

        dbrecord = self.selected_analysis.dbrecord
        if not dbrecord:
            return

#        from src.database.orms.isotope_orm import meas_AnalysisTable
#        sess = self.db.new_session()
#        self.db.sess = sess
#        q = sess.query(meas_AnalysisTable)
#        q = q.filter(meas_AnalysisTable.id == dbrecord._dbrecord.id)
#        dbr = q.one()
##        print id(dbr), dbr
#        dbrecord._dbrecord = dbr

        dbrecord.load_graph()
        dbrecord.edit_traits()

#        sess.close()
#        sess.remove()
#        self.selected_analysis.dbrecord.edit_traits()
    def set_status(self, status):
        if self.popup:
            self.popup.Close()
        dbrecord = self.selected_analysis.dbrecord
        sess = object_session(dbrecord._dbrecord)
        dbrecord._dbrecord.status = status
        sess.commit()
#        sess.close()
#        for di in dir(dbrecord._dbrecord):
#            print di


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

    def _add_scatter_inspector(self, container, plot, scatter,
                               group_id=0, add_tool=True,
                               popup=True,
                               value_format=None):
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
            u = lambda a, b, c, d: self.update_graph_metadata(scatter, group_id, a, b, c, d)
            scatter.index.on_trait_change(u, 'metadata_changed')
            if value_format is None:
                value_format = lambda x:'{:0.5f}'.format(x)
            scatter.value_format = value_format

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

                          #setting the arrow to visible causes an error when reading with illustrator
                          #if the arrow is not drawn
                          arrow_visible=False,
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

    def _make_title(self, analyses):
        def make_bounds(gi, sep='-'):
            if len(gi) > 1:
                m = '{}{}{}'.format(gi[0], sep, gi[-1])
            else:
                m = '{}'.format(gi[0])

            return m

        def make_step_bounds(si):
            if not si:
                return
            grps = []
            a = si[0]
            pa = si[1]
            cgrp = [pa]
            for xi in si[2:]:
                if ord(pa) + 1 == ord(xi):
                    cgrp.append(xi)
                else:
                    grps.append(cgrp)
                    cgrp = [xi]
                pa = xi

            grps.append(cgrp)
            return ','.join(['{}{}'.format(a, make_bounds(gi, sep='...')) for gi in grps])

        def _make_group_title(ans):
            lns = dict()
            for ai in ans:
    #            v = '{}{}'.format(ai.aliquot, ai.step)
                v = (ai.aliquot, ai.step)
                if ai.labnumber in lns:
                    lns[ai.labnumber].append(v)
                else:
                    lns[ai.labnumber] = [v]

            skeys = sorted(lns.keys())
            grps = []
            for si in skeys:
                als = lns[si]
                sals = sorted(als, key=lambda x: x[0])
                aliquots, steps = zip(*sals)

                pa = aliquots[0]
                ggrps = []
                cgrp = [pa]
                sgrp = []
                sgrps = []

                for xi, sti in zip(aliquots[1:], steps[1:]):
                    #handle analyses with steps
                    if sti != '':
                        if not sgrp:
                            sgrp.append(xi)
                        elif sgrp[0] != xi:
                            sgrps.append(sgrp)
                            sgrp = [xi]
                        sgrp.append(sti)
                    else:
                        if sgrp:
                            sgrps.append(sgrp)
                            sgrp = []

                        if pa + 1 == xi:
                            cgrp.append(xi)
                        else:
                            ggrps.append(cgrp)
                            cgrp = [xi]

                    pa = xi

                sgrps.append(sgrp)
                ggrps.append(cgrp)
                fs = [make_bounds(gi) for gi in ggrps]

                if sgrps[0]:
                    #handle steps
                    pa = sgrps[0][0]
                    ggrps = []
                    cgrp = [sgrps[0]]
                    for sgi in sgrps[1:]:
                    #    print si
                        if pa + 1 == sgi[0]:
                            cgrp.append(sgi)
                        else:
                            grps.append(cgrp)
                            cgrp = [sgi]
                        pa = sgi[0]
                    ggrps.append(cgrp)
                    ss = ['{}-{}'.format(make_step_bounds(gi[0]),
                            make_step_bounds(gi[-1])) for gi in ggrps]
                    fs.extend(ss)

                als = ','.join(fs)

                grps.append('{}-({})'.format(si, als))

            return ', '.join(grps)

        group_ids = list(set([a.group_id for a in analyses]))
        gtitles = []
        for gid in group_ids:
            anss = [ai for ai in analyses if ai.group_id == gid]
            gtitles.append(_make_group_title(anss))

        return ', '.join(gtitles)

    def update_graph_metadata(self, scatter, group_id, obj, name, old, new):
        sorted_ans = [a for a in self.sorted_analyses if a.group_id == group_id]
        hover = scatter.value.metadata.get('hover')

        if hover:
            hoverid = hover[0]
            try:
                self._hover_cache[group_id] = hoverid
            except:
                self._hover_cache = {group_id:hoverid}

            try:
                self.selected_analysis = sa = sorted_ans[hoverid]
            except IndexError:
                return

            if not self.popup:
                self.popup = PopupWindow(None)

            value = scatter.value.get_data()[hoverid]
            name = scatter.container.y_axis.title
            value = scatter.value_format(value)
            value = '{}={}'.format(name, value)
            self._show_pop_up(self.popup, sa, value, obj)
        else:
            if self._dehover_count >= len(self._hover_cache.keys()) + 3:
                self._dehover_count = 0
            elif len(self._hover_cache.keys()):
                self._dehover_count += 1
                return

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

    def _show_pop_up(self, popup, analysis, value, obj):
        try:
            x, y = obj.metadata.get('mouse_xy')
        except Exception, e:
            popup.Close()
            return

        def make_status(s):
            ss = 'OK' if s == 0 else 'Omitted'
            return 'Status= {}'.format(ss)

        lines = [
                 '{}, {}'.format(analysis.record_id, analysis.sample),
                 analysis.age_string,
                 value,
                 make_status(analysis.status)
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

#===============================================================================
# factories
#===============================================================================
    def _get_plot_option(self, options, attr, default=None):
        option = None
        if options is not None:
            if options.has_key(attr):
                option = options[attr]

        return default if option is None else option

    def _create_grid_container(self, ngroups):
        gpi = self.graph_panel_info
        r = gpi.nrows
        c = gpi.ncols

        while ngroups > r * c:
            if gpi.fixed == 'cols':
                r += 1
            else:
                c += 1

        if ngroups == 1:
            r = c = 1

        op = GridPlotContainer(shape=(r, c),
                               bgcolor='white',
                               fill_padding=True,
                               padding_top=10
                               )
        return op, r, c

#============= EOF =============================================
