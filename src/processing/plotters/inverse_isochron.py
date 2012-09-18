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
from traits.api import HasTraits, Bool
from traitsui.api import View, Item
#============= standard library imports ========================
#============= local library imports  ==========================
from src.graph.regression_graph import RegressionGraph
from src.processing.plotters.plotter import Plotter
from src.processing.plotters.results_tabular_adapter import InverseIsochronResults
from src.graph.error_ellipse_overlay import ErrorEllipseOverlay
from chaco.array_data_source import ArrayDataSource


class InverseIsochron(Plotter):
    show_error_ellipse = Bool(False)
    def build(self, analyses, padding):
        if not analyses:
            return

        xs = [a.signals['Ar39'].uvalue / a.signals['Ar40'].uvalue for a in analyses]
        ys = [a.signals['Ar36'].uvalue / a.signals['Ar40'].uvalue for a in analyses]

        xs, xerrs = zip(*[(a.nominal_value, a.std_dev()) for a in xs])
        ys, yerrs = zip(*[(a.nominal_value, a.std_dev()) for a in ys])
#        xs = [a.signals['Ar39']. / a.signals['Ar40'].value for a in analyses]
#        ys = [a.signals['Ar36'].value / a.signals['Ar40'].value for a in analyses]
        g = RegressionGraph(container_dict=dict(padding=5,
                                               bgcolor='lightgray'
                                               ))
        g.new_plot(xtitle='39Ar/40Ar',
                   ytitle='36Ar/40Ar',
                   padding=padding
                   )

        g.set_grid_traits(visible=False)
        g.set_grid_traits(visible=False, grid='y')

        po, sc, ln = g.new_series(xs, ys,
                                  xerror=ArrayDataSource(data=xerrs),
                                  yerror=ArrayDataSource(data=yerrs),
                    type='scatter', marker='circle', marker_size=2)

        eo = ErrorEllipseOverlay(component=sc)
        sc.overlays.append(eo)



        g.set_x_limits(min=0)
        g.set_y_limits(min=0, max=1 / 100.)
        trapped_4036 = 1
        trapped_4036err = 1
        try:
            rdict = g.regression_results[0]
            try:
                coeffs = rdict['coefficients']
                cerrors = rdict['coeff_errors']
                if coeffs is not None and cerrors is not None:
                    try:
                        trapped_4036 = 1 / coeffs[-1]
                        trapped_4036 = cerrors[-1]
                    except IndexError, e:
                        print e
            except KeyError, e:
                print e
        except IndexError, e:
            print e

        self.results.append(InverseIsochronResults(
                                                   age=100,
                                                   error=0.1,
                                                   mswd=0,
                                                   trapped_4036=trapped_4036,
                                                   trapped_4036err=trapped_4036err))

        return g

    def _get_content(self):
        return Item('show_error_ellipse')


#============= EOF =============================================
