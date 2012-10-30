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
from src.graph.tools.rect_selection_tool import RectSelectionTool
from src.graph.tools.data_tool import DataTool, DataToolOverlay
from src.graph.time_series_graph import TimeSeriesGraph
from src.graph.stacked_graph import StackedGraph
from src.regression.ols_regressor import PolynomialRegressor
from src.regression.mean_regressor import MeanRegressor
import copy

class StatsFilterParameters(object):
    '''
        exclude points where (xi-xm)**2>SDx*tolerance_factor
    '''
    tolerance_factor = 3.0
    blocksize = 20

class RegressionGraph(Graph):
    filters = List
    selected_component = Any
    regressors = List
    regression_results = Event
    suppress_regression = False
    use_data_tool = True
#    fits = List
#    def clear(self):
#        super(RegressionGraph, self).clear()
#        self.regressors = []
#    def set_fits(self, fits):
#        self.fits = fits
#        for fi, pi in zip(fits, self.plots):
#            scatter = pi.plots['data'][0]
#            scatter.fit = fi
    def set_filter(self, fi, plotid=0, series=0):
        plot = self.plots[plotid]
        scatter = plot.plots['data{}'.format(series)][0]
        scatter.filter = fi
        self.redraw()

    def get_filter(self, plotid=0, series=0):
        plot = self.plots[plotid]
        scatter = plot.plots['data{}'.format(series)][0]
        return scatter.filter

    def set_fit(self, fi, plotid=0, series=0):
        plot = self.plots[plotid]
        scatter = plot.plots['data{}'.format(series)][0]
        scatter.fit = fi

        self.redraw()

    def get_fit(self, plotid=0, series=0):
        plot = self.plots[plotid]
        scatter = plot.plots['data{}'.format(series)][0]
        return scatter.fit

    def _update_graph(self, **kw):
        if self.suppress_regression:
            return

        self.regressors = []
        for plot in self.plots:
            ks = plot.plots.keys()
#            print ks
#            scatters, kkk = zip(*[(plot.plots[k][0], k) for k in ks if k.startswith('data')])
#            ind = kkk[0][-1]
#            fls = [plot.plots[kk][0] for kk in ks if kk == 'fit{}'.format(ind)]
#            uls = [plot.plots[kk][0] for kk in ks if kk == 'upper CI{}'.format(ind)]
#            lls = [plot.plots[kk][0] for kk in ks if kk == 'lower CI{}'.format(ind)]
#
#            #fls = [plot.plots[k][0] for k in ks if k.startswith('fit')]
#            #uls = [plot.plots[k][0] for k in ks if k.startswith('upper')]
#            #lls = [plot.plots[k][0] for k in ks if k.startswith('lower')]
#            for si, fl, ul, ll in zip(scatters, fls, uls, lls):
#                self._plot_regression(plot, si, fl, ul, ll)
            try:
                scatters, kkk = zip(*[(plot.plots[k][0], k) for k in ks if k.startswith('data')])
                ind = kkk[0][-1]
                fls = [plot.plots[kk][0] for kk in ks if kk == 'fit{}'.format(ind)]
                uls = [plot.plots[kk][0] for kk in ks if kk == 'upper CI{}'.format(ind)]
                lls = [plot.plots[kk][0] for kk in ks if kk == 'lower CI{}'.format(ind)]

                #fls = [plot.plots[k][0] for k in ks if k.startswith('fit')]
                #uls = [plot.plots[k][0] for k in ks if k.startswith('upper')]
                #lls = [plot.plots[k][0] for k in ks if k.startswith('lower')]
                for si, fl, ul, ll in zip(scatters, fls, uls, lls):
                    self._plot_regression(plot, si, fl, ul, ll)
            except ValueError, e:
#                print e
                break
        else:
            self.regression_results = self.regressors

    def _plot_regression(self, plot, scatter, line, uline, lline):
        try:

#            sel = scatter.index.metadata.get('selections', [])
            args = self._regress(
#                                 selection=sel,
                                           plot=plot,
                                           fit=scatter.fit,
                                           filterstr=scatter.filter,
                                           filter_outliers=scatter.filter_outliers,
                                           index=scatter.index,
                                           x=scatter.index.get_data(),
                                           y=scatter.value.get_data(),
                                           )
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

    def _regress(self,
                 x, y,
#                 x=None, y=None,
#                 selection=None,
                 plotid=0,
                 plot=None,
                 index=None,
                 filter_outliers=None,
#                 component=None,
                 filterstr=None,
                 fit=None):

        fit = self._convert_fit(fit)
        if fit is None:
            return

        if plot is None:
            plot = self.plots[plotid]

#        if x is None or y is None:
#            x = plot.data.get_data('x0')
#            y = plot.data.get_data('y0')
#        print selection
#        if not selection:

        if filterstr:
            selection = self._apply_filter(filterstr, x)
            meta = dict(selections=selection)
            index.trait_set(metadata=meta, trait_change_notify=False)
        else:
            selection = index.metadata.get('selections', [])

        if filter_outliers:
            x, y, excludes = self._apply_filter_outliers(x, y)
            sels = index.metadata['selections']
            excludes = list(set(sels + excludes))
            meta = dict(selections=excludes)
            index.trait_set(metadata=meta, trait_change_notify=False)

        if selection:
            x = delete(x[:], selection, 0)
            y = delete(y[:], selection, 0)

        low = plot.index_range.low
        high = plot.index_range.high
        if fit in [1, 2, 3]:
            if len(y) < fit + 1:
                return
            st = low
            xn = x - st

            r = PolynomialRegressor(xs=xn, ys=y,
                                    degree=fit)
            self.regressors.append(r)
            fx = linspace(0, (high - low), 200)

            fy = r.predict(fx)

            if fy is None:
                return

            ci = r.calculate_ci(fx)
            if ci is not None:
                ly, uy = ci
            else:
                ly, uy = fy, fy
            fx += low

        else:
            r = MeanRegressor(xs=x, ys=y)
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

    def _apply_filter_outliers(self, xs, ys):
        '''
            filter data using stats
            
            1. group points into blocks
            2. find mean of block
            3. find outliers
            4. exclude outliers
        '''
        import numpy as np
        sf = StatsFilterParameters()
        blocksize = sf.blocksize
        tolerance_factor = sf.tolerance_factor

        #group into blocks
        n = ys.shape[0]
        r = n / blocksize
        c = blocksize

        dev = n - (r * c)
        remainder_block = None
        if dev:
            ys = ys[:-dev]
            remainder_block = ys[-dev:]
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
        inc_r, inc_c = np.where(devs <= tol)
        ny = blocks[inc_r, inc_c]
        nx = xs[inc_c + inc_r * blocksize]
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

        return nx, ny, exc_xs

    def new_series(self, x=None, y=None,
                   ux=None, uy=None, lx=None, ly=None,
                   fx=None, fy=None,
                   fit='linear',
                   filter_outliers=False,
                   marker='circle',
                   marker_size=2,
                   plotid=0, *args, **kw):

#        self.filters.append(None)
        kw['marker'] = marker
        kw['marker_size'] = marker_size
        if not fit:
            return super(RegressionGraph, self).new_series(x, y,
                                                           plotid=plotid,
                                                           *args, **kw)

        kw['type'] = 'scatter'
        plot, names, rd = self._series_factory(x, y, plotid=plotid, **kw)
        si = len([p for p in plot.plots.keys() if p.startswith('data')])

        rd['selection_color'] = 'red'
        rd['selection_marker'] = marker
        rd['selection_marker_size'] = marker_size + 2

        scatter = plot.plot(names, **rd)[0]
        self.set_series_label('data{}'.format(si), plotid=plotid)
        scatter.index.on_trait_change(self._update_graph, 'metadata_changed')

        scatter.fit = fit
        scatter.filter = None
        scatter.filter_outliers = filter_outliers

        if x is not None and y is not None:
            args = self._regress(x, y, plotid=plotid)
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

        self._add_tools(scatter, plotid)
        return plot, scatter, line

    def _add_tools(self, scatter, plotid):
        plot = self.plots[plotid]

        broadcaster = BroadcasterTool()
        self.plots[plotid].container.tools.append(broadcaster)

        rect_tool = RectSelectionTool(scatter,
#                                      parent=self,
                                      plot=plot,
                                      plotid=plotid)
        scatter.overlays.append(rect_tool)

        #add a broadcaster so scatterinspector and rect selection will received events
        broadcaster.tools.append(rect_tool)
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
