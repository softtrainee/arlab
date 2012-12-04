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
from traits.api import HasTraits, List, Any, Event
from traitsui.api import View, Item, TableEditor
from src.graph.graph import Graph
#============= standard library imports ========================
from numpy import linspace, random, hstack, polyval, \
    delete, bitwise_and, polyfit, ones, invert, average
from chaco.tools.broadcaster import BroadcasterTool
#============= local library imports  ==========================
from src.graph.tools.rect_selection_tool import RectSelectionTool, \
    RectSelectionOverlay
from src.graph.tools.data_tool import DataTool, DataToolOverlay
from src.graph.time_series_graph import TimeSeriesGraph
from src.graph.stacked_graph import StackedGraph
from src.regression.ols_regressor import PolynomialRegressor
from src.regression.mean_regressor import MeanRegressor
import copy
from src.graph.context_menu_mixin import RegressionContextMenuMixin
from enable.font_metrics_provider import font_metrics_provider

class StatsFilterParameters(object):
    '''
        exclude points where (xi-xm)**2>SDx*tolerance_factor
    '''
    tolerance_factor = 3.0
    blocksize = 20

class RegressionGraph(Graph, RegressionContextMenuMixin):
    filters = List
    selected_component = Any
    regressors = List
    regression_results = Event
    suppress_regression = False
    use_data_tool = True
    popup = None
#    fits = List
#    def clear(self):
#        super(RegressionGraph, self).clear()
#        self.regressors = []
#    def set_fits(self, fits):
#        self.fits = fits
#        for fi, pi in zip(fits, self.plots):
#            scatter = pi.plots['data'][0]
#            scatter.fit = fi

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
        scatter = plot.plots['data{}'.format(series)][0]
        scatter.fit = fi
        scatter.index.metadata['selections'] = []
        self.redraw()

    def get_fit(self, plotid=0, series=0):
        try:
            plot = self.plots[plotid]
            scatter = plot.plots['data{}'.format(series)][0]
            return scatter.fit
        except IndexError:
            pass

    def _update_graph(self, obj=None, name=None, old=None, new=None):
        if self.suppress_regression:
            print 'speunca'
            return

        self.regressors = []
        for plot in self.plots:
            ks = plot.plots.keys()
            try:
                scatters, kkk = zip(*[(plot.plots[k][0], k) for k in ks if k.startswith('data')])
            except:
                return

        regress = True
#        for si in scatters:
#            if self

        if not regress:
            return

        for plot in self.plots:
            ks = plot.plots.keys()
            try:
                scatters, kkk = zip(*[(plot.plots[k][0], k) for k in ks if k.startswith('data')])
                ind = kkk[0][-1]
                fls = [plot.plots[kk][0] for kk in ks if kk == 'fit{}'.format(ind)]
                uls = [plot.plots[kk][0] for kk in ks if kk == 'upper CI{}'.format(ind)]
                lls = [plot.plots[kk][0] for kk in ks if kk == 'lower CI{}'.format(ind)]

                for si, fl, ul, ll in zip(scatters, fls, uls, lls):
                    self._plot_regression(plot, si, fl, ul, ll)

            except ValueError, e:
                print e
                break
        else:
#            regress = True
#            if regress:
#                for plot in self.plots:
#                    for si, fl, ul, ll in zip(scatters, fls, uls, lls):
#                        self._plot_regression(plot, si, fl, ul, ll)
            self.regression_results = self.regressors

    def _plot_regression(self, plot, scatter, line, uline, lline):
        try:
#            print id(plot), plot.visible
            if not plot.visible:
                self.regressors.append(None)
                return

#            print scatter.visible
#            sel = scatter.index.metadata.get('selections', [])
#            args = self._regress(
##                                 selection=sel,
#                                           plot=plot,
##                                           fit=scatter.fit,
##                                           filterstr=scatter.filter,
##                                           filter_outliers=scatter.filter_outlier,
##                                           index=scatter.index,
#                                           scatter,
#                                           x=scatter.index.get_data(),
#                                           y=scatter.value.get_data(),
#                                           )
            args = self._regress(plot, scatter)

            if args:
                fx, fy, ly, uy = args
                line.index.set_data(fx)
                line.value.set_data(fy)

                lline.index.set_data(fx)
                lline.value.set_data(ly)

                uline.index.set_data(fx)
                uline.value.set_data(uy)
        except KeyError:
            pass

#    def _regress(self,
#                 x, y,
##                 x=None, y=None,
##                 selection=None,
#                 plotid=0,
#                 plot=None,
#                 index=None,
#                 filter_outlier_dict=None,
##                 component=None,
#                 filterstr=None,
#                 fit=None):
    def _regress(self, plot, scatter, filterstr=None):
        x = scatter.index.get_data()
        y = scatter.value.get_data()
        index = scatter.index

        fit = scatter.fit
        fod = scatter.filter_outliers_dict

        ox = x[:]
        oy = y[:]
        fit = self._convert_fit(fit)
        if fit is None:
            return

#        if plot is None:
#            plot = self.plots[plotid]

#        if x is None or y is None:
#            x = plot.data.get_data('x0')
#            y = plot.data.get_data('y0')
#        print selection
#        if not selection:

        if filterstr:
            selection = self._apply_filter(filterstr, x)
            meta = dict(selections=selection)
            index.trait_set(metadata=meta, trait_change_notify=False)
#        else:
#        print fod
        meta = index.metadata
        apply_filter = False
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
                          mouse_xy=meta.get('mouse_xy', None),
                          filtered=None
                       )
#            index.trait_set(metadata=nmeta, trait_change_notify=False)
            index.trait_set(metadata=nmeta)
#            nmeta = meta['mouse_xy']
#            meta['selections'] = sel
#            meta['filtered'] = None

        else:
            if 'filtered' in meta:
                apply_filter = True if meta['filtered'] is None else False
            else:
                apply_filter = True

        selection = meta.get('selections', [])
#        filtered = index.metadata.get('filtered', [])

#        print selection
        if selection:
#            #dont delete the selections that are also in filtered
#            selection = list(set(selection))# - set(filtered))
#
            x = delete(x[:], selection, 0)
            y = delete(y[:], selection, 0)
#            apply_filter = False
#        else:
#            filtered = False

        low = plot.index_range.low
        high = plot.index_range.high
        if fit in [1, 2, 3]:
            if len(y) < fit + 1:
                return

            st = low
            xn = x - st
#            ox = xn[:]
            r = PolynomialRegressor(xs=xn, ys=y,
                                    degree=fit)
            fx = linspace(0, (high - low), 200)

#            print r.predict(0), 'pos0', id(self)
            fy = r.predict(fx)

            if fy is None:
                return

            ci = r.calculate_ci(fx)
            if ci is not None:
                ly, uy = ci
            else:
                ly, uy = fy, fy

            fx += low
            if apply_filter:
                r = self._apply_outlier_filter(r, ox, oy, index, fod)
#            else:
#                index.metadata['selections'] = []
#            try:
#                if fod['filter_outliers']:
##                if not filtered:
#                    r = self._apply_outlier_filter(r, ox, oy, index, fod)
#                else:
#                    index.metadata['selections'] = []
#            except (KeyError, TypeError):
#                index.metadata['selections'] = []
#                index.metadata['filtered'] = []
#                meta = dict(selections=[], filtered=[])
#                index.trait_set(metadata=meta)

#            r = self._apply_outlier_filter(r, ox, oy, index, fit, include=True)

#            if selection:
#                x = delete(x[:], selection, 0)
#                y = delete(y[:], selection, 0)

            self.regressors.append(r)
        else:
            r = MeanRegressor(xs=x, ys=y)
            if apply_filter:
                r = self._apply_outlier_filter(r, ox, oy, index, fod)
#            else:
#                index.metadata['selections'] = []

#            try:
#                if fod['filter_outliers']:
##                if not filtered:
#                    r = self._apply_outlier_filter(r, ox, oy, index, fod)
#                else:
#                    index.metadata['selections'] = []
#            except (KeyError, TypeError):
#                index.metadata['selections'] = []
#                index.metadata['filtered'] = []
#                meta = dict(selections=[], filtered=[])
#                index.trait_set(metadata=meta)

            self.regressors.append(r)
            n = 10
            fx = linspace(low, high, n)
            m = r.coefficients[0]
#            print fit, fit.endswith("SEM")
            fit = fit.lower()
            if fit.endswith('sem'):
                s = r.coefficient_errors[1]
                r.error_calc = 'sem'
            else:
                r.error_calc = 'sd'
                s = r.coefficient_errors[0]

            fy = ones(n) * m
            uy = fy + s
            ly = fy - s

        return fx, fy, ly, uy

    def _apply_outlier_filter(self, reg, ox, oy, index, fod):

        try:
            if fod['filter_outliers']:
#                print 'fff'
#                if not filtered:
#                r = self._apply_outlier_filter(r, ox, oy, index, fod)
                t_fx, t_fy = ox[:], oy[:]
                niterations = fod['filter_outlier_iterations']
                n = fod['filter_outlier_std_devs']

                for ni in range(niterations):
                    excludes = list(reg.calculate_outliers(n=n))
                    oxcl = excludes[:]
                    sels = index.metadata['selections']

        #            if not include:
                    excludes = sorted(list(set(sels + excludes)))
#                    meta = dict(selections=excludes, filtered=oxcl)
                    index.metadata['filtered'] = oxcl
                    index.metadata['selections'] = excludes
#                    index.trait_set(metadata=meta, 
#                                    trait_change_nofity=ni == niterations - 1)
        #                            , trait_change_notify = False)
        #            else:
        #                print 'exc', excludes
        #                print 'sel', sels
        ##                sels = set(excludes) ^ set(sels)
        ##                print sels
        #                meta = dict(selections=[], filtered=[])
        #                index.trait_set(metadata=meta, trait_change_notify=False)

                    t_fx = delete(t_fx, excludes, 0)
                    t_fy = delete(t_fy, excludes, 0)
                    reg.trait_set(xs=t_fx, ys=t_fy)
        #            reg = reg.__class__(xs=t_fx, ys=t_fy,
        #                            degree=fit)
            else:
                pass
#                meta = index.metadata
##                if 'filtered' in meta:
##                    fpts = set(meta['filtered'])
##                    csel = set(meta['selections'])
##                    sel = list(csel - fpts)
##
##                else:
##                    sel = []
#
#                index.metadata['selections'] = []

        except (KeyError, TypeError):
            index.metadata['selections'] = []
            index.metadata['filtered'] = []
#            meta = dict(selections=[], filtered=[])
#            index.trait_set(metadata=meta)

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

            else:
                f = None

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


#    @classmethod
#    def _apply_fit_filter(cls, x, y, r):
#        '''
#            r=regressor
#        '''
#        return r.calculate_outliers()


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

            #group into blocks
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

            #calculate stats
            block_avgs = average(blocks, axis=1)
            block_stds = np.std(blocks, axis=1)
            devs = (blocks - block_avgs.reshape(r, 1)) ** 2
    #        devs = abs(blocks - block_avgs.reshape(r, 1))

            #find outliers
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

    def new_series(self, x=None, y=None,
                   ux=None, uy=None, lx=None, ly=None,
                   fx=None, fy=None,
                   fit='linear',
                   filter_outliers_dict=None,
#                   filter_outliers=True,
#                   filter_outliers=False,
                   marker='circle',
                   marker_size=2,
                   plotid=0, *args, **kw):

        kw['marker'] = marker
        kw['marker_size'] = marker_size
#        self.filters.append(None)

        if not fit:
            return super(RegressionGraph, self).new_series(x, y,
                                                           plotid=plotid,
                                                           *args, **kw)

        kw['type'] = 'scatter'
        plot, names, rd = self._series_factory(x, y, plotid=plotid, **kw)
        si = len([p for p in plot.plots.keys() if p.startswith('data')])

        rd['selection_color'] = 'white'
        rd['selection_marker'] = marker
        rd['selection_marker_size'] = marker_size + 1
        rd['selection_outline_color'] = 'red'

        scatter = plot.plot(names, **rd)[0]
        self.set_series_label('data{}'.format(si), plotid=plotid)

#        scatter.index.on_trait_change(self._update_graph, 'metadata_changed')
#        u = lambda obj, name, old, new: self._update_metadata(scatter, obj, name, old, new)
#        scatter.index.on_trait_change(u, 'metadata_changed')

        if filter_outliers_dict is None:
            filter_outliers_dict = dict(filter_outliers=False)

        scatter.fit = fit
        scatter.filter = None
        scatter.filter_outliers_dict = filter_outliers_dict

        if x is not None and y is not None:
            args = self._regress(plot, scatter)
            if args:
                fx, fy, ly, uy = args

        kw['color'] = 'black'
        kw['type'] = 'line'
        kw['render_style'] = 'connectedpoints'
        plot, names, rd = self._series_factory(fx, fy, plotid=plotid, **kw)
        line = plot.plot(names, **rd)[0]
        self.set_series_label('fit{}'.format(si), plotid=plotid)

        kw['color'] = 'red'
        plot, names, rd = self._series_factory(fx, uy, line_style='dash', plotid=plotid, **kw)
        plot.plot(names, **rd)[0]
        self.set_series_label('upper CI{}'.format(si), plotid=plotid)

        plot, names, rd = self._series_factory(fx, ly, line_style='dash', plotid=plotid, **kw)
        plot.plot(names, **rd)[0]
        self.set_series_label('lower CI{}'.format(si), plotid=plotid)

        try:
            self._set_bottom_axis(plot, plot, plotid)
        except:
            pass

        self._bind_index(scatter, **kw)
        self._add_tools(scatter, plotid)
        return plot, scatter, line

    def _bind_index(self, scatter, **kw):
        index = scatter.index
        index.on_trait_change(self._update_graph, 'metadata_changed')

        u = lambda **kw:self._update_info(scatter, **kw)
        scatter.value.on_trait_change(u, 'metadata_changed')

    def _update_info(self, scatter):
        hover = scatter.value.metadata.get('hover', None)
#        print hover
        if hover:
            hover = hover[0]
            from src.canvas.popup_window import PopupWindow
            if not self.popup:
                self.popup = PopupWindow(None)

            mouse_xy = scatter.index.metadata.get('mouse_xy')
            if mouse_xy:
                x = scatter.index.get_data()[hover]
                y = scatter.value.get_data()[hover]
                self._show_pop_up(self.popup, x, y, mouse_xy)
        else:
            if self.popup:
                self.popup.Freeze()
                self.popup.Show(False)
                self.popup.Thaw()

    def _show_pop_up(self, popup, index, value, mxmy):
        x, y = mxmy
        lines = [
                 'x={:0.1f}'.format(index),
                 'y={:0.5f}'.format(value)
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


    def _add_tools(self, scatter, plotid):
        plot = self.plots[plotid]

#        broadcaster = BroadcasterTool()
#        self.plots[plotid].container.tools.append(broadcaster)

        rect_tool = RectSelectionTool(scatter,
                                      plot=plot,
                                      plotid=plotid,
                                      container=self.plotcontainer,
#                                      update_mouse=False
                                      )
        rect_overlay = RectSelectionOverlay(
                                            tool=rect_tool)

        scatter.tools.append(rect_tool)
        scatter.overlays.append(rect_overlay)

#        print scatter.tools
        #add a broadcaster so scatterinspector and rect selection will received events
#        broadcaster.tools.append(rect_tool)
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
    def _bind_index(self, scatter, bind_selection=True, **kw):
        super(StackedRegressionGraph, self)._bind_index(scatter)
        if bind_selection:
            scatter.index.on_trait_change(self._update_metadata, 'metadata_changed')

    def _update_metadata(self, obj, name, old, new):
        self.suppress_regression = True
        for plot in self.plots:
            ks = plot.plots.keys()
            scatters = [plot.plots[k][0] for k in ks if k.startswith('data')]
            for si in scatters:
                if not si.index is obj:
                    pass
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

        self.suppress_regression = False

class StackedRegressionTimeSeriesGraph(StackedRegressionGraph, TimeSeriesGraph):
    pass

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
