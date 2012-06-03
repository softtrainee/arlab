#===============================================================================
# Copyright 2011 Jake Ross
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



#=============enthought library imports=======================
from traits.api import  Bool, Int, List, Any
from traitsui.api import View, Item, VSplit, ListEditor
from chaco.api import ScatterInspectorOverlay
#from chaco.abstract_overlay import AbstractOverlay
#=============standard library imports =======================
from numpy import delete
import time
#cos = np.cos
#sin = np.sin

#=============local library imports  ==========================
from graph import Graph
from src.graph.stacked_graph import StackedGraph
from src.data_processing.regression.regressor import Regressor
from editors.regression_editor import RegressionEditor
from tools.rect_selection_tool import RectSelectionTool


class RegressionGraph(Graph):
    '''
    '''
    selected_plotid = Int(-1)
    selected = Any
    show_regression_editor = Bool(True)

#    regression_group_editor = Instance(RegressionGroupEditor)
#    
#    regression_editor = Instance(RegressionEditor)
    #update_flag = Bool
    #prev_ind = None
    regression_editors = List(RegressionEditor)
    hover_index = Any
    last_regress_time = None

#    regressed = True 
    regression_results = None
    fit_types = []

    use_error = False

    def get_intercept(self, plotid=0):
        results = self.regression_results[plotid]
        if  results is not None:
            coeffs = results['coefficients']
            if coeffs is not None:
                return coeffs[-1]

    def _selected_plotid_changed(self):
        '''
        '''
        try:
            self.selected = self.regression_editors[self.selected_plotid]
        except IndexError:
            pass

    def __init__(self, *args, **kw):
        '''
        '''
        super(RegressionGraph, self).__init__(*args, **kw)
        self.regressor = Regressor()
        self.fit_types = []
        self.regression_results = []

    def _set_limits(self, *args, **kw):
        '''
        '''
        super(RegressionGraph, self)._set_limits(*args, **kw)
        self._metadata_changed(None, None, None)

    def _metadata_changed(self, *args, **kw):
        '''
        '''
        t = time.time()
        if self.last_regress_time is None:
            self.last_regress_time = t

        elif (t < self.last_regress_time or
                abs(t - self.last_regress_time) < 0.75):
            return

        self.last_regress_time = t

        if self.selected_plotid is -1:
            for i, p in enumerate(self.plots):
                self.regress_plot(p, i)
        else:
            plot = self.plots[self.selected_plotid]
            self.regress_plot(plot, self.selected_plotid)

    def regress_plot(self, plot, plotid):

        if 'plot0' in plot.plots:

            scatter = plot.plots['plot0'][0]
            line = plot.plots['plot1'][0]
            uline = plot.plots['plot2'][0]
            lline = plot.plots['plot3'][0]
            sel_ind = scatter.index.metadata.get('selections', [])
            if len(sel_ind) == 0:
                sel_ind = None

            x1 = line.index_range.low
            x2 = line.index_range.high

            args = self._regress_(sel_indices=sel_ind, plotid=plotid, data_range=(x1, x2))
            line.index.set_data(args['x'])
            line.value.set_data(args['y'])

            uline.index.set_data(args['upper_x'])
            uline.value.set_data(args['upper_y'])

            lline.index.set_data(args['lower_x'])
            lline.value.set_data(args['lower_y'])

            #hover hook
            hover = scatter.index.metadata.get('hover', [])
            if hover:
                self.hover_index = hover[0]
            else:
                self.hover_index = None

    def _get_type_dict(self, type):
        '''
        '''
        kw = dict()
        if 'average' in type:
            kw['use_stderr'] = True if 'SEM' in type else False
            type = 'average'
        elif type is 'custom':
            fitfunc = eval('lambda p,x:%s' % self.fitfunc)

            type = 'least_squares'
            kw['fitfunc'] = fitfunc
            kw['errfunc'] = lambda p, x, y: fitfunc(p, x) - y
            kw['p0'] = self.initial_guess

        return type, kw

    def _regress_(self, sel_indices=None, plotid=None, data_range=None):
        '''
        '''
        if sel_indices is None:
            sel_indices = []
        if plotid is None:
            plotid = self.selected_plotid

        plot = self.plots[plotid]
        dplot = plot.plots['plot0'][0]

        data_range = (dplot.index_range.low, dplot.index_range.high)

#        fitdata = np.delete(dplot.value.get_data(), sel_indices, 0)
#        indexdata = np.delete(dplot.index.get_data(), sel_indices, 0)
        fitdata = delete(dplot.value.get_data(), sel_indices, 0)
        indexdata = delete(dplot.index.get_data(), sel_indices, 0)

#        if self.use_error:
#            fiterrdata = self.get_data(axis = 2)

        type = self.fit_types[plotid]
        type, kw = self._get_type_dict(type)

#        type = 'weighted_least_squares'
#        type = 'least_squares'
#        kw = {}
#        kw['fitfunc'] = fitfunc = lambda c, x:c[0] * x + c[1]
#        kw['errfunc'] = lambda c, x, y: fitfunc(c, x) - y
#        kw['fiterrdata'] = fiterrdata
#        kw['p0'] = [1, 1]
        r = getattr(self.regressor, type)

        kw['data_range'] = data_range
        return_dict = r(indexdata, fitdata, **kw)

        if self.show_regression_editor and return_dict:

            editor = self.regression_editors[plotid]
            editor.set_regression_statistics(return_dict, plotid=plotid)

        self.regression_results[plotid] = return_dict
        return return_dict

    def add_datum(self, *args, **kw):
        '''
        '''
        super(RegressionGraph, self).add_datum(*args, **kw)
        self._metadata_changed()
        #self.regress_plot(plot, plotid)
#        args = self._regress_(**kw)
#        if args:
#            self.set_data(args['x'], series = 1, **kw)
#            self.set_data(args['y'], series = 1, axis = 1, **kw)

    def calc_residuals(self, plotid=0, split=False):
        '''

        '''
        x, y, res = None, None, None
        plots = self.plots[plotid].plots
        if 'plot0' in plots:
            dplot = plots['plot0'][0]

            x = dplot.index.get_data()
            y = dplot.value.get_data()
            res = []
            if len(x) > 0 and len(y) > 0:
                s = dplot.index.metadata.get('selections')
                dr = (dplot.index_range.low, dplot.index_range.high)
#                xd = np.delete(x, s, 0)
#                yd = np.delete(y, s, 0)
                xd = delete(x, s, 0)
                yd = delete(y, s, 0)

                type = self.fit_types[plotid]
                type, kw = self._get_type_dict(type)
                res = self.regressor.calc_residuals(x, y, xd, yd, type, **kw)
            else:
                x = []
                y = []

        return x, y, res

    def new_plot(self, **kw):
        '''

        '''
        self.regression_results.append(None)
        super(RegressionGraph, self).new_plot(**kw)
        if self.show_regression_editor:

            self.regression_editors.append(RegressionEditor(graph=self,
                                                            id=len(self.regression_editors)))

    def new_series(self, x=None, y=None, plotid=0, fit_type='linear', regress=True, *args, **kw):
        '''
        '''
        if not regress:
            return super(RegressionGraph, self).new_series(x=x, y=y, plotid=plotid, *args, **kw)

        kw['type'] = 'scatter'
        plot, names, rd = self._series_factory(x, y, plotid=plotid, **kw)
        scatter = plot.plot(names, **rd)[0]
        self.set_series_label('data')
#        si = ScatterTool(component = scatter,
#                         selection_color = 'blue'
#                         )#, parent = self, plotid = plotid)
#     #   scatter.tools.append(si)

        overlay = ScatterInspectorOverlay(component=scatter,
                                        hover_color='green',
                                #        hover_metadata_name = 'no',
                                        selection_color='red',
                                        )
        scatter.overlays.append(overlay)

        scatter.index.on_trait_change(self._metadata_changed,
                                            'metadata_changed')

        rect_tool = RectSelectionTool(scatter, parent=self, plotid=plotid)
        scatter.overlays.append(rect_tool)

        #rect_tool.on_trait_change(self._metadata_changed, 'update_flag')

        kw['type'] = 'line'
        kw['render_style'] = 'connectedpoints'

        self.fit_types.append(fit_type)

        if x is not None and y is not None:
            args = self._regress_(plotid=plotid)
            x = args['x']
            y = args['y']
            ux = args['upper_x']
            uy = args['upper_y']
            lx = args['lower_x']
            ly = args['lower_y']

        else:
            x = None
            y = None
            ux = None
            uy = None
            lx = None
            ly = None

        plot, names, rd = self._series_factory(x, y, plotid=plotid, **kw)
        line = plot.plot(names, **rd)[0]
        self.set_series_label('fit', series=1)
        if 'color' in kw:
            kw.pop('color')

        plot, names, rd = self._series_factory(ux, uy, line_style='dash', color='red', plotid=plotid, **kw)
        plot.plot(names, **rd)[0]
        self.set_series_label('upper CI', series=2)

        plot, names, rd = self._series_factory(lx, ly, line_style='dash', color='red', plotid=plotid, **kw)
        plot.plot(names, **rd)[0]
        self.set_series_label('lower CI', series=3)

        return plot, scatter, line

    def traits_view(self):
        '''
        '''
        v = super(RegressionGraph, self).traits_view()
        v.content.content.height = 0.75
        if self.show_regression_editor:
            grp = VSplit(
                       #Group(
                       v.content,
                       Item('regression_editors',
                            style='custom',
                            editor=ListEditor(use_notebook=True,
                                                selected='selected'),
                            show_label=False,
                            height=0.25
                            ),
                        )
            v = View(grp, resizable=True,
                     title=self.window_title,
                   width=self.window_width,
                   height=self.window_height)
        return v


class StackedRegressionGraph(RegressionGraph, StackedGraph):
    pass

if __name__ == '__main__':
    r = RegressionGraph()
    r.new_plot()

#    p='/Users/fargo2/Pychrondata_beta/data/sandbox/April 11 Faraday air labbook/7_H1_39.txt'
#    xs = np.linspace(2, 10, 30)
#    fitfunc = lambda p, x: p[0] * x ** 2 + p[1] * x + p[2]
#    p = [1, 3, 4]
#    ys = fitfunc(p, xs) + 2 * np.random.randn(len(xs))

    xs = [0, 1, 2, 3, 4, 5]
    ys = [xi * 2 + 3 for xi in xs]
    ys[0] = 5
    yer = [1, 1, 1, 1, 1, 1]  # [0.2, 0.2, 0.4, 0.3, 0.6]
    from src.data_processing.regression.ols import WLS

    w = WLS(xs, ys, yer)

#    xs=[]
#    ys=[]
#    import csv
#    with open(p,'r') as f:
#        reader=csv.reader(f,delimiter='\t')
#        reader.next()
#        for x,y,err in reader:
#            xs.append(float(x))
#            ys.append(float(y))
#    
#    reg=Regressor()
#    reg.exponential(xs, ys)
#    
    r.new_series(xs, ys, yer=yer, marker='circle', marker_size=1.5)
    r.configure_traits()
#============= EOF ====================================
