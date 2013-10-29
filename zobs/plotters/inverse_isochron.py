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
from traits.api import Bool
from chaco.array_data_source import ArrayDataSource
#============= standard library imports ========================
#============= local library imports  ==========================
from src.graph.regression_graph import RegressionGraph
from src.processing.plotters.plotter import Plotter
from src.processing.plotters.results_tabular_adapter import InverseIsochronResults
from src.graph.error_ellipse_overlay import ErrorEllipseOverlay
from src.regression.new_york_regressor import NewYorkRegressor
# from src.regression.york_regressor import YorkRegressor


class InverseIsochron(Plotter):
    show_error_ellipse = Bool(False)

    def build(self, analyses, options=None, plotter_options=None):
        if not analyses:
            return

        xx = [a.Ar39 / a.Ar40 for a in analyses]
        yy = [a.Ar36 / a.Ar40 for a in analyses]
        xs, xerrs = zip(*[(xi.nominal_value, xi.std_dev) for xi in xx])
        ys, yerrs = zip(*[(yi.nominal_value, yi.std_dev) for yi in yy])
        #         print xerrs, yerrs
        #        xs, xerrs = zip(*[(a.nominal_value, a.std_dev()) for a in
        #                          [a.arar_result['s39'] / a.arar_result['s40'] for a in analyses]
        #                          ])
        #        ys, yerrs = zip(*[(a.nominal_value, a.std_dev()) for a in
        #                          [a.arar_result['s36'] / a.arar_result['s40'] for a in analyses]])

        g = RegressionGraph(container_dict=dict(padding=5,
                                                bgcolor='lightgray'
        ),

        )
        g.new_plot(xtitle='39Ar/40Ar',
                   ytitle='36Ar/40Ar',
                   padding_let=60
        )

        g.set_grid_traits(visible=False)
        g.set_grid_traits(visible=False, grid='y')

        po, sc, ln = g.new_series(xs, ys,
                                  xerror=ArrayDataSource(data=xerrs),
                                  yerror=ArrayDataSource(data=yerrs),
                                  type='scatter', marker='circle', marker_size=2)

        eo = ErrorEllipseOverlay(component=sc)
        sc.overlays.append(eo)


        #        trapped_4036 = 1
        #        trapped_4036err = 1
        #            rdict = g.regression_results[0]
        #         reg = g.regressors[0]
        reg = NewYorkRegressor(xs=xs, ys=ys, xserr=xerrs, yserr=yerrs)

        trapped_4036 = 1 / reg.predict()
        trapped_4036err = reg.predict_error()
        #         trapped_4036 = 1 / reg.coefficients[0]
        #         trapped_4036err = reg.coefficient_errors[0]

        g.add_horizontal_rule(1 / 295.5)

        #         txt = u'Trapped 40Ar= {:0.2f} {}{:0.7f}'.format(trapped_4036, PLUSMINUS, trapped_4036err)
        txt = u'Trapped 40Ar= {:0.2f} +/-{:0.7f}'.format(trapped_4036, trapped_4036err)

        g.add_plot_label(txt, 0, 0)
        g.set_x_limits(min_=0)
        g.set_y_limits(min_=0, max_=0.004)
        g.refresh()

        return g


#============= EOF =============================================
