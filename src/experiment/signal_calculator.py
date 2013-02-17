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
from traits.api import HasTraits, Str, Float, on_trait_change, Instance, List, Enum
from traitsui.api import View, Item, HGroup, VGroup, spring, Group, ListEditor, InstanceEditor
#============= standard library imports ========================
import numpy as np
import math
#============= local library imports  ==========================
from src.processing.arar_constants import ArArConstants
from src.graph.graph import Graph
from chaco.axis import PlotAxis
from chaco.plot_factory import create_line_plot, add_default_axes
from src.graph.guide_overlay import GuideOverlay

class Index(HasTraits):
    name = Str
    start = Float(0)
    end = Float(0.25)

    def calculate(self, age, sensitivity, k2o):
        c = ArArConstants()
        xs = np.linspace(self.start, self.end)
        ys = [self._calculate(wi, age, sensitivity, k2o, c) for wi in xs]
        return xs, ys, xs

    def _calculate(self, w, age, sensitivity, k2o, c):
        moles_40k = w / 1000. *k2o / 100. * 1 / c.mK * (2 * c.mK) / (2 * c.mK + c.mO) * c.abundance_40K
        moles_40Ar = moles_40k * (math.exp(c.lambda_k.nominal_value * age * 1e6) - 1) * (c.lambda_e_v / c.lambda_k.nominal_value)
        return moles_40Ar / sensitivity


class WeightIndex(Index):
    name = 'Weight'
    def traits_view(self):
        v = View(Item('start', label='Weight Start (mg)'),
#                        spring,
                 Item('end', label='Weight End (mg)'))
        return v

class VolumeIndex(Index):
    name = 'Volume'
    depth = Float(0.1) #mm
    rho = 2580 #kg/m^3
    shape = Enum('circle', 'square')
    def traits_view(self):
        v = View(Item('start', label='Dimension Start (mm)'),
                 Item('end', label='Dimension End (mm)'),
                 HGroup(Item('shape'), Item('depth', label='Depth (mm)')),
                 )
        return v

    def calculate(self, age, sensitivity, k2o):
        c = ArArConstants()
        xs = np.linspace(self.start, self.end)

        def to_weight(d, depth, rho):
            '''
                d== mm
                depth==mm
                rho==kg/m^3
            '''
            #convert dimension to meters
            d = d / 1000.
            depth = depth / 1000.
            if self.shape == 'circle':
                v = math.pi * (d / 2.) ** 2 * depth
            else:
                v = d ** 2 * depth

            m = rho * v
            #convert mass to mg 1e6 mg in 1 kg
            return m * 1e6

        #convert dim to weight
        ws = [to_weight(di, self.depth, self.rho) for di in xs]

        ys = [self._calculate(wi, age, sensitivity, k2o, c) for wi in ws]
        return xs, ys, ws

    def _shape_default(self):
        return 'circle'

class SignalCalculator(HasTraits):
    age = Float(28.2)
    k2o = Float #percent
    sensitivity = Float(5e-17) #moles/fA

    graph = Instance(Graph)
    weight_index = Instance(WeightIndex, ())
    volume_index = Instance(VolumeIndex, ())
    kind = Enum('weight', 'volume')

    def _kind_changed(self):
        if self.kind == 'weight':
            self.secondary_plot.visible = False
#            self.secondary_plot.y_axis.visible = False
        else:
            self.secondary_plot.visible = True
#            self.secondary_plot.y_axis.visible = True

        self._calculate()

    @on_trait_change('weight_index:+,volume_index:+,sensitivity, k2o, age')
    def _calculate(self):
        '''
            calculate signal size for n mg of sample with m k2o of age p 
        '''
        if self.kind == 'weight':
            attr = self.weight_index
            self.graph.set_x_title('weight (mg)')
        else:
            self.graph.set_x_title('dimension (mm)')
            attr = self.volume_index

        xs, ys, yy = attr.calculate(self.age, self.sensitivity, self.k2o)
        self.graph.set_data(xs)
        self.graph.set_data(ys, axis=1)
        self.graph.redraw()

        self.secondary_plot.value.set_data(yy)
        self.secondary_plot.index.set_data(xs)

    def traits_view(self):
        cntrl_grp = VGroup(
                           Item('age', label='Age (Ma)'),
                           HGroup(Item('k2o', label='K2O %'),
                                  spring,
                                  Item('sensitivity', label='Sensitivity (mol/fA)')),

                           Item('kind'),
                           Item('volume_index', show_label=False, style='custom',
                                visible_when='kind=="volume"'),
                           Item('weight_index', show_label=False, style='custom',
                                visible_when='kind=="weight"'),

                           )

        graph_grp = VGroup(Item('graph',
                                width=500,
                                height=500,
                                show_label=False, style='custom'),)
        v = View(
                 VGroup(cntrl_grp, graph_grp),
                 resizable=True,
                 title='Signal Calculator'
                 )
        return v

    def _graph_default(self):
        g = Graph(container_dict=dict(padding=5))
        g.new_plot(xtitle='weight (mg)', ytitle='Signal (fA)',
                   padding=[60, 60, 10, 60]
                   )

        g.new_series()

        fp = create_line_plot(([], []), color='black')
        left, bottom = add_default_axes(fp)
        bottom.visible = False
        left.orientation = 'right'
        left.axis_line_visible = False

        left.title = 'Weight (mg)'
        if self.kind == 'weight':
            fp.visible = False

        g.plots[0].add(fp)
        self.secondary_plot = fp

        return g

    def _kind_default(self):
        return 'weight'

if __name__ == '__main__':
    sc = SignalCalculator()
    sc.configure_traits()
#============= EOF =============================================
