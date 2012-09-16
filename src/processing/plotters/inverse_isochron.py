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
from traits.api import HasTraits
#============= standard library imports ========================
#============= local library imports  ==========================
from src.graph.regression_graph import RegressionGraph

class InverseIsochron(object):
    def build(self, analyses, padding):
        if not analyses:
            return

        xs = [a.signals['Ar39'].value / a.signals['Ar40'].value for a in analyses]
        ys = [a.signals['Ar36'].value / a.signals['Ar40'].value for a in analyses]
        g = RegressionGraph(container_dict=dict(padding=5,
                                               bgcolor='lightgray'
                                               ))
        g.new_plot(xtitle='39Ar/40Ar',
                   ytitle='36Ar/40Ar',
                   padding=padding
                   )

        g.set_grid_traits(visible=False)
        g.set_grid_traits(visible=False, grid='y')

        g.new_series(xs, ys,
                    type='scatter', marker='circle', marker_size=2)

        g.set_x_limits(min=0)
        g.set_y_limits(min=0, max=1 / 100.)
        return g

#============= EOF =============================================
