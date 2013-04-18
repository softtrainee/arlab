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
from traits.api import Property, List, Any, Dict, Instance
from traitsui.api import View, Item, VGroup, TabularEditor
from chaco.array_data_source import ArrayDataSource
from chaco.tools.broadcaster import BroadcasterTool
from chaco.plot_containers import GridPlotContainer
from chaco.data_label import DataLabel
from chaco.tools.data_label_tool import DataLabelTool
from sqlalchemy.orm.session import object_session
# from chaco.scatterplot import ScatterPlot
#============= standard library imports ========================
from numpy import array
#============= local library imports  ==========================
from src.viewable import Viewable
from src.processing.plotters.results_tabular_adapter import ResultsTabularAdapter, \
    BaseResults
from src.graph.error_bar_overlay import ErrorBarOverlay
from src.graph.tools.rect_selection_tool import RectSelectionTool, \
    RectSelectionOverlay
# from enable.font_metrics_provider import font_metrics_provider
# from src.canvas.popup_window import PopupWindow
from src.graph.context_menu_mixin import IsotopeContextMenuMixin
from src.graph.stacked_graph import StackedGraph
from src.processing.plotters.graph_panel_info import GraphPanelInfo
from src.graph.tools.point_inspector import PointInspectorOverlay
from src.graph.tools.analysis_inspector import AnalysisPointInspector
from src.helpers.formatting import floatfmt
from src.constants import PLUSMINUS


class mStackedGraph(StackedGraph, IsotopeContextMenuMixin):
    plotter = Any
    selected_analysis = Property
    def _get_selected_analysis(self):
        if self.plotter:
            if self.plotter.selected_analysis:
                if hasattr(self.plotter.selected_analysis, 'isotope_record'):
                    return self.plotter.selected_analysis

    def set_status_omit(self):
        self.plotter.set_status(1)

    def set_status_include(self):
        self.plotter.set_status(0)

    def set_status_void(self):
        self.plotter.set_status(-1)

    def recall_analysis(self):
        self.plotter.recall_analysis()

    def edit_analyses(self):
        self.plotter.edit_analyses()

class mDataLabelTool(DataLabelTool):
    def normal_left_down(self, event):
        if self.is_draggable(event.x, event.y):
            event.handled = True

    def normal_mouse_move(self, event):
        if self.is_draggable(event.x, event.y):
            event.window.set_pointer('arrow')
            event.handled = True

class Plotter(Viewable):
    adapter = Property
    results = List(BaseResults)
    graphs = List
#    graph = Any
    db = Any
    processing_manager = Any
    selected_analysis = Any
    analyses = Any
    sorted_analyses = Property(depends_on='analyses')
    error_bar_overlay = Any
    figure = Any
    graph_panel_info = Instance(GraphPanelInfo, ())

    options = None
    plotter_options = None

    padding = List([60, 10, 5, 40])

    metadata_label_text = Property

    def edit_analyses(self):
        self.processing_manager.edit_analyses()

    def recall_analysis(self):
        iso_record = self.selected_analysis.isotope_record
        if not iso_record:
            return

        if iso_record.initialize():
            iso_record.load_graph()
            iso_record.edit_traits()

    def set_status(self, status):
        sa = self.selected_analysis
        if status == -1:
            status_str = 'void'
        elif status == 0:
            status_str = 'including'
        else:
            status_str = 'omitting'

        self.info('{} analysis {}'.format(status_str, sa.record_id))
        dbrecord = sa.dbrecord
        sess = object_session(dbrecord)
        dbrecord.status = status
        sa.temp_status = status

        sess.commit()

        group_id = sa.group_id
        graph_id = sa.graph_id
        ans = self._get_sorted_analyses()
        pt = ans.index(sa)
        if status == 0:
            self._modify_excluded_point('remove', pt, group_id, graph_id)
        else:
            self._modify_excluded_point('append', pt, group_id, graph_id)

    def set_excluded_points(self, exclude, group_id, graph_id=0):
        if not exclude:
            return

        graph = self.graphs[graph_id]

        try:
            plot = graph.plots[1].plots['plot{}'.format(group_id)][0]
            plot.index.metadata['selections'] = exclude
        except IndexError, e:
            print e

    def build(self, analyses=None,
              options=None,
              plotter_options=None,
              new_container=True
              ):

        if analyses is None:
            analyses = self.analyses

        if options is None:
            options = self.options
        if plotter_options is None:
            plotter_options = self.plotter_options

        self.options = options
        self.plotter_options = plotter_options
        self.analyses = analyses

        graph_ids = sorted(list(set([a.graph_id for a in analyses])))
        def get_analyses(gii):
            return [a for a in analyses if a.graph_id == gii]

        graph_groups = [get_analyses(gi)
                            for gi in graph_ids]
        self._ngroups = n = len(graph_groups)

        op, r, c = self._create_grid_container(n)
        if new_container:
            self._plotcontainer = op
        else:
            op = self._plotcontainer
            op.remove(*op.components)

        self.graphs = []
        self.results = []
        plots = []

        title = self._get_plot_option(options, 'title')
        aux_plots = self._assemble_aux_plots(plotter_options)

        xtick_font = self._get_plot_option(plotter_options, 'xtick_font', 'helvetica 10')
        xtitle_font = self._get_plot_option(plotter_options, 'xtitle_font', 'helvetica 10')
        ytick_font = self._get_plot_option(plotter_options, 'ytick_font', 'helvetica 10')
        ytitle_font = self._get_plot_option(plotter_options, 'ytitle_font', 'helvetica 10')
#        xtick_font = plotter_options.xtick_font
#        xtitle_font = plotter_options.xtitle_font
#        ytick_font = plotter_options.ytick_font
#        ytitle_font = plotter_options.ytitle_font

        age_unit = analyses[0].age_units
        for i in range(r):
            for j in range(c):
                k = i * c + j
                try:
                    ans = graph_groups[k]
                except IndexError:
                    break

                g = self._build(ans, aux_plots=aux_plots,
                                title=title
                                )
                if i == r - 1:
                    self._build_xtitle(g, xtitle_font, xtick_font, age_unit=age_unit)

                if j == 0:
                    self._build_ytitle(g, ytitle_font, ytick_font, aux_plots, age_unit=age_unit)

                for pi in g.plots:
                    pi.y_axis.tick_in = False

                op.add(g.plotcontainer)
                self.graphs.append(g)
                for pi in g.plots:
                    plots.append(pi)

        op.invalidate_and_redraw()
        self._plots = plots
        return op, plots

    def _assemble_aux_plots(self, po):
        aux = []
        if po is not None:
            aux_plots = po.get_aux_plots()
            if aux_plots is None:
                aux_plots = []

            aux_plots = self._filter_aux_plots(aux_plots)
            for ap in aux_plots:
#                if isinstance(ap, str):
#                    name = ap
#                    scale = 'linear'
#                    height = 100
#                    xerror = False
#                else:
                name = ap.name
                scale = ap.scale
                height = ap.height
                x_error = ap.x_error
                y_error = ap.y_error

                if name == 'radiogenic':
                    d = dict(name='radiogenic_percent',
                              ytitle='40Ar* %',
                              )
                elif name == 'analysis_number':
                    d = dict(name='analysis_number',
                         ytitle='Analysis #',
                         )
                elif name == 'kca':
                    d = dict(name='kca',
                         ytitle='K/Ca',
                         )
                elif name == 'moles_K39':
                    d = dict(name='moles_K39',
                             ytitle='K39 moles'
                             )
                else:
                    continue

                d['height'] = height
                d['scale'] = scale
                d['x_error'] = x_error
                d['y_error'] = y_error
                aux.append(d)
        return aux

    def _build_xtitle(self, *args, **kw):
        pass
    def _build_ytitle(self, *args, **kw):
        pass

    def _build(self, analyses, aux_plots=None, title=''):
        if aux_plots is None:
            aux_plots = []

        g = mStackedGraph(panel_height=200,
                            equi_stack=False,
                            container_dict=dict(padding=0),
                            plotter=self
                            )
        g.clear()
#        g.plotcontainer.tools.append(TraitsTool(g.plotcontainer))
        g._has_title = True

        p = g.new_plot(padding=self.padding, title=None if aux_plots else title)
        p.value_range.tight_bounds = False

        self._build_aux_plots(g, aux_plots, title)

        g.set_grid_traits(visible=False)
        g.set_grid_traits(visible=False, grid='y')
        self._build_hook(g, analyses, aux_plots=aux_plots)
        return g

    def _filter_aux_plots(self, aux_plots):
        return aux_plots

    def _build_aux_plots(self, g, aux_plots, title):
        for i, ap in enumerate(aux_plots):
            kwargs = dict(padding=self.padding,
                          bounds=[50, ap['height']])

            if i == len(aux_plots) - 1:
                kwargs['title'] = title

            p = g.new_plot(**kwargs)
            if ap['scale'] == 'log':
                p.value_range.tight_bounds = True
            else:
                p.value_range.tight_bounds = False

    def _modify_excluded_point(self, func, point, group_id, graph_id=0):
        graph = self.graphs[graph_id]
        try:
            plot = graph.plots[1].plots['plot{}'.format(group_id)][0]
            selection = plot.index.metadata['selections']
            ffunc = getattr(selection, func)
            ffunc(point)

            # force scatterplot to compute selection cache
            plot._selection_cache_valid = False

        except IndexError, e:
            print e

        self._update_graph(graph)

#    def _get_ages_errors(self, analyses, group_id=0):
#        nages, nerrors = zip(*[(a.age.nominal_value, a.age.std_dev())
#                                   for a in analyses if a.group_id == group_id])
#        return array(nages), array(nerrors)
    def _get_ages(self, analyses, group_id=None, unzip=True):
        if group_id is not None:
            analyses = [ai for ai in analyses if ai.group_id == group_id]

        ije = self.plotter_options.include_j_error
        iie = self.plotter_options.include_irradiation_error
        ide = self.plotter_options.include_decay_error
#        for ai in analyses:
#            ai.age_dirty = True
#            ai.include_decay_error = True
#            print 'setting', id(ai), ai.include_decay_error
#            ai.trait_set(include_j_error=ije,
#                         include_irradiation_error=iie,
#                         include_decay_error=ide,
#                         )

        ages = [ai.calculate_age(include_j_error=ije,
                         include_irradiation_error=iie,
                         include_decay_error=ide) for ai in analyses]

        if unzip:

            ages, errors = zip(*[(a.nominal_value, a.std_dev)
                                 for a in ages])
            ages = array(ages)
            errors = array(errors)
            return ages, errors
        else:
            return ages
#    def _get_adapter(self):
#        return ResultsTabularAdapter
#
#    def _get_toolbar(self):
#        return
#
#    def _get_content(self):
#        content = Item('results',
#                      style='custom',
#                      show_label=False,
#                      editor=TabularEditor(adapter=self.adapter(),
#                                           auto_update=True
#                                           ),
#                       height=50
#                       )
#        return content

    def _add_error_bars(self, scatter, errors, axis, nsigma):
        ebo = ErrorBarOverlay(component=scatter, orientation=axis, nsigma=nsigma)
        scatter.underlays.append(ebo)
        setattr(scatter, '{}error'.format(axis), ArrayDataSource(errors))
#        if sigma_trait:
#            self.on_trait_change(ebo.update_sigma, sigma_trait)

    def _add_scatter_inspector(self, container, plot, scatter,
                               group_id=0,
                               add_tool=True,
#                               popup=True,
                               value_format=None,
                               additional_info=None
                               ):
        # add a scatter hover tool
#        bc = BroadcasterTool()
#        broadcaster = BroadcasterTool()
#        scatter.tools.append(broadcaster)
#        self.plots[plotid].container.tools.append(broadcaster)
#        scatter.tools.append(ScatterInspector(scatter,
# #                                              selection_mode='off'
#                                              ))

#        broadcaster.tools.append(ScatterInspector(scatter,
# #                                              selection_mode='off'
#                                              ))

#        rect_tool = RectSelectionTool(scatter,
# #                                      parent=self,
# #                                      plot=self.graph.plots[0],
#                                      plotid=1
#                                      )
        if add_tool:
#            rect_tool = RectSelectionTool(scatter,
#    #                                      parent=self,
#                                          container=container,
#                                          plot=plot,
#                                          group_id=group_id
#    #                                      plotid=1
#                                          )
#            rect_overlay = RectSelectionOverlay(
#                                                tool=rect_tool)
#            scatter.tools.append(rect_tool)
#            scatter.overlays.append(rect_overlay)
            broadcaster = BroadcasterTool()
            scatter.tools.append(broadcaster)

            rect_tool = RectSelectionTool(scatter)
            rect_overlay = RectSelectionOverlay(tool=rect_tool)

            scatter.overlays.append(rect_overlay)
            broadcaster.tools.append(rect_tool)

            if value_format is None:
                value_format = lambda x:'{:0.5f}'.format(x)
            point_inspector = AnalysisPointInspector(scatter,
                                                     analyses=[a for a in self.sorted_analyses
                                                                    if a.group_id == group_id],
                                                     convert_index=lambda x: '{:0.3f}'.format(x),
                                                     value_format=value_format,
                                                     additional_info=additional_info
                                                     )

            pinspector_overlay = PointInspectorOverlay(component=scatter,
                                                       tool=point_inspector,
                                                       )
#
            scatter.overlays.append(pinspector_overlay)
            broadcaster.tools.append(point_inspector)

            u = lambda a, b, c, d: self.update_graph_metadata(scatter, group_id, a, b, c, d)
            scatter.index.on_trait_change(u, 'metadata_changed')
#        scatter.overlays.append(rect_tool)
#        overlay = ScatterInspectorOverlay(scatter,
#                    hover_color="red",
#                    hover_marker_size=int(scatter.marker_size + 2),
                    # selection_color='transparent',
                    # selection_marker_size=int(scatter.marker_size),
                    # selection_marker=scatter.marker
#                    selection_outlin
#                    )
#        scatter.overlays.append(overlay)
#        if popup:
#            u = lambda a, b, c, d: self.update_graph_metadata(scatter, group_id, a, b, c, d)
#            scatter.index.on_trait_change(u, 'metadata_changed')


#        self.metadata = scatter.index.metadata
    def _add_data_label(self, s, text, point, bgcolor='transparent',
                        label_position='top right', color=None, append=True, **kw):
        if color is None:
            color = s.color

        label = DataLabel(component=s, data_point=point,
                          label_position=label_position,
                          label_text=text,
                          border_visible=False,
                          bgcolor=bgcolor,
                          show_label_coords=False,
                          marker_visible=False,
                          text_color=color,

                          # setting the arrow to visible causes an error when reading with illustrator
                          # if the arrow is not drawn
                          arrow_visible=False,
                          **kw
                          )
        s.overlays.append(label)
        tool = mDataLabelTool(label)
        if append:
            label.tools.append(tool)
        else:
            label.tools.insert(0, tool)
        return label

    def _get_sorted_analyses(self):
        return sorted([a for a in self.analyses], key=self._cmp_analyses)

    def get_labnumber(self, analyses):
        return ', '.join(sorted(list(set(['{}-{}'.format(a.labnumber, a.aliquot) for a in analyses]))))

    def update_graph_metadata(self, scatter, group_id, obj, name, old, new):
        sorted_ans = [a for a in self.sorted_analyses if a.group_id == group_id]
#        hover = scatter.value.metadata.get('hover')
        hover = scatter.index.metadata.get('hover')
        if hover:
            hoverid = hover[0]
            try:
                self.selected_analysis = sorted_ans[hoverid]
            except IndexError:
                return
        else:
            self.selected_analysis = None

        sel = obj.metadata.get('selections', [])
        # set the temp_status for all the analyses
        for i, a in enumerate(sorted_ans):
            a.temp_status = 1 if i in sel else 0

    def _cmp_analyses(self, x):
        return x.timestamp

    def _update_graph(self, graph):
        pass

    def _build_label_text(self, x, we, mswd, valid_mswd, n):
        display_n = True
        display_mswd = n >= 2
        if display_n:
            n = 'n= {}'.format(n)
        else:
            n = ''

        if display_mswd:
            vd = '' if valid_mswd else '*'
            mswd = '{}mswd= {:0.2f}'.format(vd, mswd)
        else:
            mswd = ''

        x = floatfmt(x, 3)
        we = floatfmt(we, 4)
        return u'{} {}{} {} {}'.format(x, PLUSMINUS, we, mswd, n)
    def _unzip_value_error(self, pairs):
#        mk39, mk39_errs = zip(*[(ri.nominal_value, ri.std_dev()) for ri in mk39])
        return zip(*[(ri.nominal_value, ri.std_dev) for ri in pairs])

    def _add_plot_metadata(self, g):
        # add meta plot info
        font = self._get_plot_option(self.options, 'metadata_label_font', default='modern 10')
        ustr = self.metadata_label_text
#        ustr = u'data 1s, age {}s'.format(self.plotter_options.nsigma)
#        self.plot_label = g.add_plot_label(self.plot_label_text, 0, 0, font=font)
        self.plot_label = g.add_plot_label(ustr, 0, 0, font=font)

    def _get_grouped_analyses(self):
        analyses = self.analyses
        group_ids = list(set([a.group_id for a in analyses]))

        return [[ai for ai in analyses if ai.group_id == gid]
                for gid in group_ids
                ]
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
            if isinstance(options, dict):
                if options.has_key(attr):
                    option = options[attr]
            else:
                if hasattr(options, attr):
                    option = getattr(options, attr)

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
#    def _show_pop_up(self, popup, analysis, value, obj):
#        try:
#            x, y = obj.metadata.get('mouse_xy')
#        except Exception, e:
#            popup.Close()
#            return
#
#        def make_status(s):
#            ss = 'OK' if s == 0 else 'Omitted'
#            return 'Status= {}'.format(ss)
#
#        lines = [
#                 '{}, {}'.format(analysis.record_id, analysis.sample),
#                 analysis.age_string,
#                 value,
#                 make_status(analysis.status)
#               ]
#        t = '\n'.join(lines)
#        gc = font_metrics_provider()
#        with gc:
#            font = popup.GetFont()
#            from kiva.fonttools import Font
#            gc.set_font(Font(face_name=font.GetFaceName(),
#                             size=font.GetPointSize(),
#                             family=font.GetFamily(),
# #                             weight=font.GetWeight(),
# #                             style=font.GetStyle(),
# #                             underline=0,
# #                             encoding=DEFAULT
#                             ))
#            linewidths, lineheights = zip(*[gc.get_full_text_extent(line)[:2]  for line in lines])
# #            print linewidths, lineheights
#            ml = max(linewidths)
#            mh = max(lineheights)
#
# #        ch = popup.GetCharWidth()
#        mh = mh * len(lines)
# #        print ml, mh
# #        popup.Freeze()
#        popup.SetPosition((x + 55, y + 25))
#        popup.set_size(ml, mh)
#        popup.SetText(t)
#        popup.Show(True)
# #        popup.Thaw()
