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
from traits.api import List, Any, Event
from chaco.tools.broadcaster import BroadcasterTool
#============= standard library imports ========================
from numpy import linspace, random, \
    delete, bitwise_and, invert, average
import weakref

#============= local library imports  ==========================
from src.graph.graph import Graph
from src.graph.tools.rect_selection_tool import RectSelectionTool, \
    RectSelectionOverlay
from src.graph.time_series_graph import TimeSeriesGraph
from src.graph.stacked_graph import StackedGraph
from src.regression.ols_regressor import PolynomialRegressor
from src.regression.mean_regressor import MeanRegressor
from src.graph.context_menu_mixin import RegressionContextMenuMixin
from src.graph.tools.regression_inspector import RegressionInspectorTool, \
    RegressionInspectorOverlay
from src.graph.tools.point_inspector import PointInspector, \
    PointInspectorOverlay
from src.regression.wls_regressor import WeightedPolynomialRegressor
from src.regression.least_squares_regressor import LeastSquaresRegressor
from src.regression.base_regressor import BaseRegressor
from src.graph.error_envelope_overlay import ErrorEnvelopeOverlay


class NoRegressionCTX(object):
    def __init__(self, obj, refresh=False):
        self._refresh = refresh
        self._obj = obj

    def __enter__(self):
        self._obj.suppress_regression = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._obj.suppress_regression = False
        if self._refresh:
            self._obj.refresh()


class StatsFilterParameters(object):
    '''
        exclude points where (xi-xm)**2>SDx*tolerance_factor
    '''
    tolerance_factor = 3.0
    blocksize = 20


class RegressionGraph(Graph, RegressionContextMenuMixin):
    indices = List
    filters = List
    selected_component = Any
    regressors = List
    regression_results = Event
    suppress_regression = False

    use_data_tool = True
    use_inspector_tool = True
    use_point_inspector = True

    #===============================================================================
    # context menu handlers
    #===============================================================================
    def cm_linear(self):
        self.set_fit('linear')
        self._update_graph()

    def cm_parabolic(self):
        self.set_fit('parabolic')
        self._update_graph()

    def cm_cubic(self):
        self.set_fit('cubic')
        self._update_graph()

    def cm_average_std(self):
        self.set_fit('average_std')
        self._update_graph()

    def cm_average_sem(self):
        self.set_fit('average_sem')
        self._update_graph()

    #===============================================================================
    #
    #===============================================================================

    def set_filter(self, fi, plotid=0, series=0):
        plot = self.plots[plotid]
        scatter = plot.plots['data{}'.format(series)][0]
        scatter.filter = fi
        self.redraw()

    def set_filter_outliers(self, fi, plotid=0, series=0):
        plot = self.plots[plotid]
        scatter = plot.plots['data{}'.format(series)][0]
        scatter.filter_outliers_dict['filter_outliers'] = fi
        #        scatter.index.metadata['selections'] = []

        self.redraw()

    def get_filter_outliers(self, fi, plotid=0, series=0):
        plot = self.plots[plotid]
        scatter = plot.plots['data{}'.format(series)][0]
        return scatter.filter_outliers_dict['filter_outliers']

    #        scatter.filter_outliers = fi
    #        self.redraw()

    def get_filter(self, plotid=0, series=0):
        plot = self.plots[plotid]
        scatter = plot.plots['data{}'.format(series)][0]
        return scatter.filter

    def set_fit(self, fi, plotid=0, series=0):
        plot = self.plots[plotid]

        key = 'data{}'.format(series)
        #         print plot.plots.keys(), key, plot.plots.has_key(key), fi
        if plot.plots.has_key(key):
            scatter = plot.plots[key][0]
            if scatter.fit != fi:
                lkey = 'line{}'.format(series)
                if plot.plots.has_key(lkey):
                    line = plot.plots[lkey][0]
                    line.regressor = None

                scatter.fit = fi
                scatter.index.metadata['selections'] = []
                scatter.index.metadata['filtered'] = None
                self.redraw()

    def get_fit(self, plotid=0, series=0):
        try:
            plot = self.plots[plotid]
            scatter = plot.plots['data{}'.format(series)][0]
            return scatter.fit
        except IndexError:
            pass

    def clear(self):
        self.regressors = []

        #x = self.indices[:]
        #for idx in x:
        #    idx.on_trait_change(self.update_metadata,
        #                        'metadata_changed', remove=True)
        #    self.indices.remove(idx)
        #del x
        self.selected_component = None

        for p in self.plots:
            for pp in p.plots.values():
                if hasattr(pp, 'error_envelope'):
                    pp.error_envelope.component = None
                    del pp.error_envelope

                if hasattr(pp, 'regressor'):
                    del pp.regressor

        super(RegressionGraph, self).clear()

    def no_regression(self, refresh=False):
        return NoRegressionCTX(self, refresh=refresh)

    def refresh(self, **kw):
        self._update_graph()

    def update_metadata(self, obj, name, old, new):
        """
            fired when the index metadata changes e.i user selection
        """
        #print obj, name, old, new
        sel = obj.metadata.get('selections', None)
        #
        if sel:
            obj.was_selected = True
            self._update_graph()
        elif hasattr(obj, 'was_selected'):
            if obj.was_selected:
                self._update_graph()
            obj.was_selected = False

    def _update_graph(self, *args, **kw):
        if self.suppress_regression:
            return

        #self.regressors = []
        regs = []
        for plot in self.plots:
            ps = plot.plots
            ks = ps.keys()
            try:
                scatters, idxes = zip(*[(ps[k][0], k[4:]) for k in ks if k.startswith('data')])
                idx = idxes[0]
                fls = (ps[kk][0] for kk in ks if kk == 'fit{}'.format(idx))

                for si, fl in zip(scatters, fls):
                    r = self._plot_regression(plot, si, fl)
                    regs.append(r)

            except ValueError, e:
                break

        self.regressors = regs
        self.regression_results = regs

    def _plot_regression(self, plot, scatter, line):
    #         try:
        if not plot.visible:
            self.regressors.append(None)
            return

        return self._regress(plot, scatter, line)

    #             if args:
    #                 r, fx, fy, ly, uy = args
    #                 line.index.set_data(fx)
    #                 line.value.set_data(fy)
    #                 if hasattr(line, 'error_envelope'):
    #                     line.error_envelope.lower = ly
    #                     line.error_envelope.upper = uy
    #                     line.error_envelope.invalidate()

    #                 self.regressors.append(r)

    #         except KeyError:
    #             pass

    def _regress(self, plot, scatter, line, filterstr=None):
        x = scatter.index.get_data()
        y = scatter.value.get_data()
        index = scatter.index

        fod = scatter.filter_outliers_dict

        ox = x[:]
        oy = y[:]
        #        ox, oy = None, None
        fit = self._convert_fit(scatter.fit)
        if fit is None:
            return

        if filterstr:
            selection = self._apply_filter(filterstr, x)
            meta = dict(selections=selection)
            index.trait_set(metadata=meta, trait_change_notify=False)

        meta = index.metadata
        #        apply_filter = False
        if not fod['filter_outliers']:
            apply_filter = False
            csel = set(meta['selections'])
            sel = list(csel)
            if 'filtered' in meta:
                fpts = meta['filtered']
                if fpts:
                    fpts = set(meta['filtered'])
                    sel = list(csel - fpts)

            nmeta = dict(selections=sel,
                         filtered=None
            )
            index.trait_set(metadata=nmeta)

        else:
            if 'filtered' in meta:
                apply_filter = True if meta['filtered'] is None else False
            else:
                apply_filter = True

        selection = meta.get('selections', [])

        if selection:
            x = delete(x, selection, 0)
            y = delete(y, selection, 0)

        r = None
        if line and hasattr(line, 'regressor'):
            r = line.regressor

        if fit in [1, 2, 3]:
            if y.shape[0] < fit + 1:
                return
            r = self._poly_regress(r, x, y, ox, oy, index, fit, fod,
                                   apply_filter, scatter, selection)
        elif isinstance(fit, tuple):
            r = self._least_square_regress(r, x, y, ox, oy, index, fit, fod,
                                           apply_filter)
        elif isinstance(fit, BaseRegressor):
            r = self._custom_regress(r, x, y, ox, oy, index, fit, fod,
                                     apply_filter, scatter, selection)

        else:
            r = self._mean_regress(r, x, y, ox, oy, index, fit, fod,
                                   apply_filter)

        low = plot.index_range.low
        high = plot.index_range.high
        fx = linspace(low, high, 100)
        fy = r.predict(fx)
        if line:
            line.regressor = r

            line.index.set_data(fx)
            line.value.set_data(fy)

            if hasattr(line, 'error_envelope'):
                ci = r.calculate_ci(fx, fy)
                #                 print ci
                if ci is not None:
                    ly, uy = ci
                else:
                    ly, uy = fy, fy

                line.error_envelope.lower = ly
                line.error_envelope.upper = uy
                line.error_envelope.invalidate()

        return r
        #self.regressors.append(r)

    def _least_square_regress(self, r, x, y, ox, oy, index,
                              fit, fod, apply_filter):
        fitfunc, errfunc = fit
        if r is None or not isinstance(r, LeastSquaresRegressor):
            r = LeastSquaresRegressor()

        r.trait_set(xs=x, ys=y,
                    fitfunc=fitfunc,
                    errfunc=errfunc,
                    trait_change_notify=False
        )
        r.calculate()

        if apply_filter:
            r = self._apply_outlier_filter(r, ox, oy, index, fod)

        return r

    def _mean_regress(self, r, x, y, ox, oy, index,
                      fit, fod, apply_filter):

        if r is None or not isinstance(r, MeanRegressor):
            r = MeanRegressor()

        r.trait_set(xs=x, ys=y, fit=fit, trait_change_notify=False)
        r.calculate()

        if apply_filter:
            r = self._apply_outlier_filter(r, ox, oy, index, fod)
        return r

    def _custom_regress(self, r, x, y, ox, oy, index,
                        fit, fod, apply_filter, scatter, selection):
        kw = dict(xs=x, ys=y)
        if hasattr(scatter, 'yerror'):
            es = scatter.yerror.get_data()
            if selection:
                es = delete(es, selection, 0)
            kw['yserr'] = es

        if hasattr(scatter, 'xerror'):
            es = scatter.xerror.get_data()
            if selection:
                es = delete(es, selection, 0)
            kw['xserr'] = es

        if r is None or not isinstance(r, fit):
            r = fit()

        r.trait_set(trait_change_notify=False,
                    **kw)
        r.calculate()

        if apply_filter:
            r = self._apply_outlier_filter(r, ox, oy, index, fod)

        return r

    def _poly_regress(self, r, x, y, ox, oy, index,
                      fit, fod, apply_filter, scatter, selection):

        if hasattr(scatter, 'yerror'):
            es = scatter.yerror.get_data()
            if selection:
                es = delete(es, selection, 0)

            if r is None or not isinstance(r, WeightedPolynomialRegressor):
                r = WeightedPolynomialRegressor()

            r.trait_set(yserr=es, trait_change_notify=False)
        else:
            if r is None or not isinstance(r, PolynomialRegressor):
                r = PolynomialRegressor()

        r.trait_set(xs=x, ys=y, degree=fit,
                    trait_change_notify=False)
        #        r.degree = fit
        r.calculate()
        #print 'aaaa',r
        if apply_filter:
            r = self._apply_outlier_filter(r, ox, oy, index, fod)

        return r

    def _apply_outlier_filter(self, reg, ox, oy, index, fod):
        try:
            if fod['filter_outliers']:
            #                 t_fx, t_fy = ox[:], oy[:]
                t_fx, t_fy = ox, oy
                niterations = fod['filter_outlier_iterations']
                n = fod['filter_outlier_std_devs']
                for _ in range(niterations):
                    excludes = list(reg.calculate_outliers(nsigma=n))
                    oxcl = excludes[:]
                    sels = index.metadata['selections']

                    excludes = sorted(list(set(sels + excludes)))
                    index.metadata['filtered'] = oxcl
                    index.metadata['selections'] = excludes

                    t_fx = delete(t_fx, excludes, 0)
                    t_fy = delete(t_fy, excludes, 0)
                    reg.trait_set(xs=t_fx, ys=t_fy)

        except (KeyError, TypeError), e:
            print 'apply outlier filter', e
            index.metadata['selections'] = []
            index.metadata['filtered'] = None

        return reg

    @classmethod
    def _convert_fit(cls, f):
        if isinstance(f, str):
            f = f.lower()
            fits = ['linear', 'parabolic', 'cubic']
            if f in fits:
                f = fits.index(f) + 1
            elif 'average' in f:
                if f.endswith('sem'):
                    f = 'averageSEM'
                else:
                    f = 'averageSD'
                    #                if not (f.endswith('sd') or f.endswith('sem')):
                    #                    f = 'averageSD'
                    #            elif f in ['preceeding', 'bracketing interpolate', 'bracketing average']:
                    #                f = f
            else:
                f = None
                #        elif isinstance(f, tuple):
                #            #f == fitfunc, errfunc
                #            return f
        return f

    #    def _apply_filter(self, filt, xs, ys):
    def _apply_filter(self, filt, xs):
    #        if filt:
        '''
            100   == filters out t>100
            10,100 == fitlers out t<10 and t>100

        '''
        filt = map(float, filt.split(','))
        ge = filt[-1]
        sli = xs.__ge__(ge)

        if len(filt) == 2:
            le = filt[0]
            sli = bitwise_and(sli, xs.__ge__(le))
            if le > ge:
                return

        return list(invert(sli).nonzero()[0])

    @classmethod
    def _apply_block_filter(cls, xs, ys):
        '''
            filter data using stats
            
            1. group points into blocks
            2. find mean of block
            3. find outliers
            4. exclude outliers
        '''

        try:
            import numpy as np

            sf = StatsFilterParameters()
            blocksize = sf.blocksize
            tolerance_factor = sf.tolerance_factor

            # group into blocks
            n = ys.shape[0]
            r = n / blocksize
            c = blocksize

            dev = n - (r * c)
            #            remainder_block = None
            if dev:
                ys = ys[:-dev]
                #                remainder_block = ys[-dev:]
            #            remainder_

            blocks = ys.reshape(r, c)

            # calculate stats
            block_avgs = average(blocks, axis=1)
            block_stds = np.std(blocks, axis=1)
            devs = (blocks - block_avgs.reshape(r, 1)) ** 2
            #        devs = abs(blocks - block_avgs.reshape(r, 1))

            # find outliers
            tol = block_stds.reshape(r, 1) * tolerance_factor
            exc_r, exc_c = np.where(devs > tol)
            #            inc_r, inc_c = np.where(devs <= tol)
            #            ny = blocks[inc_r, inc_c]
            #            nx = xs[inc_c + inc_r * blocksize]
            exc_xs = list(exc_c + exc_r * blocksize)

            #        if remainder_block:
            #        #do filter on remainder block
            #            avg = average(remainder_block)
            #            stds = np.std(remainder_block)
            #            tol = stds * tolerance_factor
            #            devs = (remainder_block - avg) ** 2
            #            exc_i, _ = np.where(devs > tol)
            #            inc_i, _ = np.where(devs < tol)
            #            exc_i = exc_i + n - 1
            #            nnx = xs[inc_i + n - 1]
            #            nny = ys[inc_i + n - 1]
            #
            #            nx = hstack((nx, nnx))
            #            ny = hstack((ny, nny))
            #            exc_xs += exc_i
            #        print exc_xs
            #        return nx, ny, exc_xs
        except:
            exc_xs = []

        return exc_xs

    def _new_scatter(self, kw, marker, marker_size, plotid,
                     x, y, fit, filter_outliers_dict):
        kw['type'] = 'scatter'
        plot, names, rd = self._series_factory(x, y, plotid=plotid, **kw)

        rd['selection_color'] = 'white'
        rd['selection_outline_color'] = rd['color']
        rd['selection_marker'] = marker
        rd['selection_marker_size'] = marker_size + 1
        scatter = plot.plot(names, add=False, **rd)[0]
        si = len([p for p in plot.plots.keys() if p.startswith('data')])

        self.set_series_label('data{}'.format(si), plotid=plotid)
        if filter_outliers_dict is None:
            filter_outliers_dict = dict(filter_outliers=False)

        scatter.fit = fit
        scatter.filter = None
        scatter.filter_outliers_dict = filter_outliers_dict
        scatter.index.on_trait_change(self.update_metadata, 'metadata_changed')

        return scatter, si

    def new_series(self, x=None, y=None,
                   ux=None, uy=None, lx=None, ly=None,
                   fx=None, fy=None,
                   fit='linear',
                   filter_outliers_dict=None,
                   use_error_envelope=True,
                   #                   filter_outliers=True,
                   #                   filter_outliers=False,
                   marker='circle',
                   marker_size=2,
                   add_tools=True,
                   add_inspector=True,
                   convert_index=None,
                   plotid=0, *args,
                   **kw):

        kw['marker'] = marker
        kw['marker_size'] = marker_size

        if not fit:
            s, p = super(RegressionGraph, self).new_series(x, y,
                                                           plotid=plotid,
                                                           *args, **kw)
            if add_tools:
                self.add_tools(p, s, None, convert_index, add_inspector)
            return s, p
        
        scatter,si = self._new_scatter(kw, marker, marker_size,
                                    plotid, x, y, fit,
                                    filter_outliers_dict)
        lkw = kw.copy()
        lkw['color'] = 'black'
        lkw['type'] = 'line'
        lkw['render_style'] = 'connectedpoints'
        plot, names, rd = self._series_factory(fx, fy, plotid=plotid,
                                               **lkw)
        line = plot.plot(names,add=False, **rd)[0]
        line.index.sort_order = 'ascending'
        self.set_series_label('fit{}'.format(si), plotid=plotid)
        
        plot.add(line)
        plot.add(scatter)
        
        if use_error_envelope:
            self._add_error_envelope_overlay(line)
            
        r = None
        if x is not None and y is not None:
            if not self.suppress_regression:
                self._regress(plot, scatter, line)

        try:
            self._set_bottom_axis(plot, plot, plotid)
        except:
            pass

        self._bind_index(scatter, **kw)

        if add_tools:
            self.add_tools(plot, scatter, line,
                           convert_index, add_inspector)

        return plot, scatter, line

    #def _bind_index(self, scatter, **kw):
    #    index = scatter.index
    #    index.on_trait_change(self.update_metadata, 'metadata_changed')

    #         self.indices.append(index)

    def _add_error_envelope_overlay(self, line):

        o = ErrorEnvelopeOverlay(component=weakref.ref(line)())
        line.overlays.append(o)
        line.error_envelope = o

    def add_tools(self, plot, scatter, line=None,
                  convert_index=None, add_inspector=True):

        # add a regression inspector tool to the line
        if line:
            tool = RegressionInspectorTool(component=line)
            overlay = RegressionInspectorOverlay(component=line,
                                                 tool=tool)
            line.tools.append(tool)
            line.overlays.append(overlay)

        broadcaster = BroadcasterTool()
        scatter.tools.append(broadcaster)

        if add_inspector:
            point_inspector = PointInspector(scatter,
                                             convert_index=convert_index)
            pinspector_overlay = PointInspectorOverlay(component=scatter,
                                                       tool=point_inspector
            )
            #
            scatter.overlays.append(pinspector_overlay)
            broadcaster.tools.append(point_inspector)

        #            if line:
        #                #add a regression inspector tool to the line
        #                tool = RegressionInspectorTool(component=line)
        #                overlay = RegressionInspectorOverlay(component=line,
        #                                                 tool=tool)
        #                line.tools.append(tool)
        #                line.overlays.append(overlay)

        rect_tool = RectSelectionTool(scatter)
        rect_overlay = RectSelectionOverlay(tool=rect_tool)

        scatter.overlays.append(rect_overlay)
        broadcaster.tools.append(rect_tool)

        #

        #            print container

        #        print scatter.tools
        # add a broadcaster so scatterinspector and rect selection will received events

#        scatter.overlays.append(rect_overlay)
#        data_tool = DataTool(
#                             component=plot,
#                             plot=scatter,
#                             plotid=plotid,
#                             parent=self
#                             )
#        data_tool_overlay = DataToolOverlay(component=scatter,
#                                            tool=data_tool,
#                                            )
#        scatter.overlays.append(data_tool_overlay)
#
#        broadcaster.tools.append(data_tool)

#        if not self.use_data_tool:
#            data_tool.visible = False

#    def set_x_limits(self, *args, **kw):
#        '''
#        '''
#        super(RegressionGraph, self).set_x_limits(*args, **kw)
#        self._update_graph()


class RegressionTimeSeriesGraph(RegressionGraph, TimeSeriesGraph):
    pass


class StackedRegressionGraph(RegressionGraph, StackedGraph):
    pass

    #def _bind_index(self, scatter, bind_selection=True, **kw):
    #    super(StackedRegressionGraph, self)._bind_index(scatter)

    #        if bind_selection:

#            scatter.index.on_trait_change(self._update_metadata, 'metadata_changed')
#
#    def _update_metadata(self, obj, name, old, new):
#        self.suppress_regression = True
#        for plot in self.plots:
#            ks = plot.plots.keys()
#            scatters = [plot.plots[k][0] for k in ks if k.startswith('data')]
#            for si in scatters:
#                if not si.index is obj:
#                    pass
#                    si.index.trait_set(metadata=obj.metadata)
#                pass
#    #                print id(obj), id(si.index), si.index
#                if not si.index is obj:
#                    nn = obj.metadata.get('selections', None)
#                    try:
#                        hover = si.index.metadata['hover']
#                    except KeyError:
#                        hover = []
#                    meta = dict(bind_selection=nn,
#                                selections=si.index.metadata['selections'],
#                                hover=hover
#                                )
#                    si.index.trait_set(metadata=meta, trait_change_notify=False)
#                    si.index.metadata['bind_selection'] = nn
#                ind = si.index.clone_traits('metadata')
#                ind.metadata.update(dict(bind_s=nn))

#                print 'fff', obj.metadata['selections']
#                    si.index.trait_set(metadata=ind.metadata)
#                    si.index.metadata.update(dict(bind_s=nn))
#                    si.index.metadata['bind_s'] = nn
#                    si.index.metadata['bind_selections'] = obj.metadata['selections']
#                    si.index.trait_set(metadata=obj.metadata)
#                    si.value.trait_set(metadata=obj.metadata)

#        self.suppress_regression = False


class StackedRegressionTimeSeriesGraph(StackedRegressionGraph, TimeSeriesGraph):
    pass


# class AnnotatedRegressionGraph(HasTraits):
#    klass = RegressionGraph
#    graph = Instance(RegressionGraph)
#    display = Instance(RichTextDisplay)
#
#    graph_dict = Dict
#    display_dict = Dict
##===============================================================================
# #  view attrs
##===============================================================================
#    window_width = 500
#    window_height = 500
#    window_x = 20
#    window_y = 20
#    window_title = ' '
#    def __init__(self, graph_dict=None, display_dict=None, *args, **kw):
#        if graph_dict:
#            self.graph_dict = graph_dict
#        if display_dict:
#            self.display_dict = display_dict
#        super(AnnotatedRegressionGraph, self).__init__(*args, **kw)
#
#    @on_trait_change('graph:regression_results')
#    def _update_display(self, new):
#        if new:
#            disp = self.display
#            disp.clear()
#            for ri in new:
#                eq = ri.make_equation()
#                if eq:
#                    # mean regressor doesnt display an equation
#                    self.display.add_text(eq)
#
#                self.display.add_text(ri.tostring())
#
#    def traits_view(self):
#        v = View(Item('graph', show_label=False, style='custom'),
#               Item('display', show_label=False, style='custom'),
#               resizable=True,
#               x=self.window_x,
#               y=self.window_y,
#               width=self.window_width,
#               height=self.window_height,
#               title=self.window_title
#               )
#        return v
#
#    def _graph_default(self):
#        return self.klass(**self.graph_dict)
#
#    def _display_default(self):
#        d = RichTextDisplay(height=100,
#                            width=200,
#                            default_color='black', default_size=12)
#        return d
#
# class AnnotatedRegresssionTimeSeriesGraph(AnnotatedRegressionGraph):
#    klass = RegressionTimeSeriesGraph

if __name__ == '__main__':
    import numpy as np

    rg = RegressionGraph()
    rg.new_plot()
    x = linspace(0, 10, 200)

    y = 2 * x + random.rand(200)

    d = np.zeros(200)
    d[::10] = random.rand() * 15

    y += d
    rg.new_series(x, y, filter_outliers=True)
    rg._update_graph()
    rg.configure_traits()
#============= EOF =============================================
