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
from chaco.default_colormaps import color_map_name_dict
from traits.api import HasTraits, Instance, on_trait_change, Button, Float, Str, \
    Dict, Property, Event, Int, Bool, List
from traitsui.api import View, UItem, InstanceEditor, TableEditor, VGroup, VSplit, EnumEditor, Item
# from src.envisage.tasks.base_editor import BaseTraitsEditor
# from src.processing.tasks.analysis_edit.graph_editor import GraphEditor
from traitsui.extras.checkbox_column import CheckboxColumn
from traitsui.table_column import ObjectColumn
from src.graph.contour_graph import ContourGraph
from src.helpers.formatting import floatfmt
from src.processing.tasks.analysis_edit.graph_editor import GraphEditor
from src.processing.tasks.flux.irradiation_tray_overlay import IrradiationTrayOverlay
from src.regression.flux_regressor import BowlFluxRegressor, PlaneFluxRegressor
#============= standard library imports ========================
from numpy import linspace, array, max, zeros, meshgrid, vstack

#============= local library imports  ==========================


def make_grid(r, n):
    xi = linspace(-r, r, n)
    yi = linspace(-r, r, n)
    return meshgrid(xi, yi)


class FluxTool(HasTraits):
    calculate_button = Button('Calculate')
    monitor_age = Float
    color_map_name = Str('hot')
    levels = Int(10, auto_set=False, enter_set=True)
    model_kind = Str('Plane')

    def traits_view(self):
        v = View(
            VGroup(UItem('calculate_button'),
                   VGroup(
                       Item('color_map_name',
                            label='Color Map',
                            editor=EnumEditor(values=sorted(color_map_name_dict.keys()))),
                       Item('levels'),
                       Item('model_kind', label='Fit Model',
                            editor=EnumEditor(values=['Bowl', 'Plane']))
                   )))
        return v


#Position = namedtuple('Positon', 'position x y')

class MonitorPosition(HasTraits):
    hole_id = Int
    identifier = Str
    x = Float
    y = Float
    z = Float
    j = Float
    jerr = Float
    use = Bool(True)


class FluxEditor(GraphEditor):
    tool = Instance(FluxTool, ())
    monitor_positions = Dict

    positions_dirty = Event
    positions = Property(depends_on='positions_dirty')
    geometry = List

    def _get_positions(self):
        return sorted(self.monitor_positions.itervalues(), key=lambda x: x.hole_id)

    def add_monitor_position(self, pid, identifier, x, y, j):
        pos = MonitorPosition(identifier=identifier,
                              hole_id=pid,
                              x=x, y=y, j=j.nominal_value, jerr=j.std_dev)

        self.monitor_positions[identifier] = pos
        self.positions_dirty = True

    def _dump_tool(self):
        pass

    @on_trait_change('monitor_positions:use')
    def _handle_monitor_pos_use(self):
        print 'monitor pos change'
        self.rebuild_graph()

    @on_trait_change('tool:[color_map_name, levels, model_kind]')
    def _handle_color_map_name(self):
        self.rebuild_graph()

    def _rebuild_graph(self):
        g = self.graph

        #@todo: add a colorbar

        p = g.new_plot(xtitle='X', ytitle='Y')
        ito = IrradiationTrayOverlay(component=p,
                                     geometry=self.geometry)
        p.overlays.append(ito)

        try:
            x, y, z, ze = array([(pos.x, pos.y, pos.j, pos.jerr)
                                 for pos in self.monitor_positions.itervalues()
                                 if pos.use]).T
        except ValueError:
            self.debug('no monitor positions to fit')
            return

        if len(x) > 3:
            n = z.shape[0] * 10
            r = max((max(abs(x)), max(abs(y))))
            r *= 1.25

            gx, gy = make_grid(r, n)
            m = self._model_flux(n, x, y, gx, gy, z, ze)

            g.new_series(x, y, type='scatter',
                         marker='circle')
            g.new_series(z=m,
                         xbounds=(-r, r),
                         ybounds=(-r, r),
                         levels=self.tool.levels,
                         cmap=self.tool.color_map_name,
                         style='contour')

    def _model_flux(self, n, xx, yy, cell_x, cell_y, z, ze):

        nz = zeros((n, n))
        xy = zip(xx, yy)
        if self.tool.model_kind == 'Bowl':
            klass = BowlFluxRegressor
        else:
            klass = PlaneFluxRegressor

        reg = klass(xs=xy, ys=z, yserr=ze)

        for i in xrange(n):
            pts = vstack((cell_x[i], cell_y[i])).T
            nz[i] = reg.predict(pts)

        return nz

    def _graph_default(self):
        g = ContourGraph()

        g.new_plot(xtitle='X', ytitle='Y')

        return g

    def traits_view(self):
        cols = [
            CheckboxColumn(name='use', label='Use'),
            ObjectColumn(name='hole_id', label='Hole', editable=False),
            ObjectColumn(name='identifier', label='Identifier', editable=False),
            ObjectColumn(name='x', label='X', editable=False, format='%0.3f'),
            ObjectColumn(name='y', label='Y', editable=False, format='%0.3f'),
            ObjectColumn(name='j', label='J',
                         format_func=floatfmt,
                         editable=False),
            ObjectColumn(name='jerr',
                         format_func=floatfmt,
                         label=u'\u00b1\u03c3', editable=False)]
        editor = TableEditor(columns=cols, sortable=False, reorderable=False)

        v = View(VSplit(
            UItem('graph',
                  style='custom',
                  editor=InstanceEditor(), height=0.72),
            UItem('positions', editor=editor, height=0.28)))
        return v

        #class FluxEditor(InterpolationEditor):
        #    level = Any
        #    tool = Instance(FluxTool, ())
        #
        #    def _dump_tool(self):
        #        pass
        #
        #    def _rebuild_graph(self):
        #        g = self.graph
        #        if self.references:
        #            p = g.new_plot(xtitle='Hole Position (radians)',
        #                           ytitle='Flux',
        #                           padding=[70, 10, 10, 60])
        #            p.index_range.tight_bounds = False
        #            reg2D = self._model_flux()
        #
        #            xs = reg2D.xs
        #            skw = dict(type='scatter', marker='circle', marker_size=2)
        #            scatter, _ = g.new_series(xs, reg2D.ys, yerror=reg2D.yserr,
        #                                      **skw)
        #            ebo = ErrorBarOverlay(component=scatter, orientation='y')
        #            scatter.overlays.append(ebo)
        #            self._add_inspector(scatter)
        #
        #            # plot fit
        #            xs = linspace(min(xs), max(xs))
        #
        #            ys = reg2D.predict(xs)
        #            g.new_series(xs, ys, color='black')
        #
        #            es = reg2D.predict_error(xs, ys)
        #
        #            g.new_series(xs, ys + es, color='red')
        #            g.new_series(xs, ys - es, color='red')
        #
        #            #            # plot predicted unknowns
        #            uxs = self._get_xs(self.unknowns)
        #            ys = reg2D.predict(uxs)
        #            es = reg2D.predict_error(uxs, ys)
        #            scatter, _ = g.new_series(uxs, ys, yerror=es, **skw)
        #
        #            ebo = ErrorBarOverlay(component=scatter, orientation='y')
        #            scatter.overlays.append(ebo)
        #            self._add_inspector(scatter)
        #
        #    def _add_inspector(self, scatter):
        #        from src.graph.tools.point_inspector import PointInspector
        #        from src.graph.tools.point_inspector import PointInspectorOverlay
        #
        #        point_inspector = PointInspector(scatter)
        #        pinspector_overlay = PointInspectorOverlay(component=scatter,
        #                                                   tool=point_inspector)
        #        #
        #        scatter.overlays.append(pinspector_overlay)
        #        scatter.tools.append(point_inspector)
        #
        #    def _model_flux(self):
        #        fitfunc = lambda p, x: p[0] * cos(p[1] * x + p[2]) + p[3] * x + p[4]
        #
        #        x = self._get_xs(self._references)
        #        #        x, y, e = zip(*[(ri.position, ri.labnumber.selected_flux_history.flux.j,
        #        #                      ri.labnumber.selected_flux_history.flux.j_err)
        #        #                      for ri in self._references])
        #        y, e = self._get_flux(self._references)
        #        reg2D = LeastSquaresRegressor(
        #            fitfunc=fitfunc,
        #            xs=x, ys=y, yserr=e,
        #            initial_guess=[1, 1, 1, 1, 1],
        #        )
        #        reg2D.calculate()
        #        return reg2D
        #
        #    def _get_flux(self, ans):
        #        y, e = zip(*[(ri.labnumber.selected_flux_history.flux.j,
        #                      ri.labnumber.selected_flux_history.flux.j_err)
        #                     for ri in ans])
        #        return y, e
        #
        #    def _get_xs(self, ans):
        #        xy = self._get_xy(ans)
        #        return [math.atan2(x, y) for x, y in xy]
        #
        #    def _get_xy(self, ans):
        #xx = []
        #if self.level:
        #    geom = self.level.holder.geometry
        #
        #    positions = [
        #        Position(i, x, y)
        #        for i, (x, y) in enumerate([struct.unpack('>ff', geom[i:i + 8]) for i in xrange(0, len(geom), 8)])
        #    ]
        #    for ri in ans:
        #        pos = next((pi for pi in positions if pi.position + 1 == ri.position), None)
        #        if pos:
        #        #                    print ri.position, pos.x, pos.y, math.atan2(pos.x, pos.y)
        #            xx.append((pos.x, pos.y))
        #return xx

#
#    @on_trait_change('unknowns[]')
#    def _update_unknowns(self):
#
#
#        '''
#            TODO: find reference analyses using the current _unknowns
#        '''
#        #         self._make_unknowns()
#        self.rebuild_graph()
#
#    #     def _make_unknowns(self):
#    #         self._unknowns = self.unknowns
#
#    #     def make_references(self):
#    #         self._references = self.references
#
#    def _graph_default(self):
#        g = Graph()
#        return g


#============= EOF =============================================
