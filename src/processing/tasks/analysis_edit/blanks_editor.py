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
from traits.api import HasTraits, Instance, Str, Bool, List, implements, on_trait_change, \
    Any, Event
from traitsui.api import View, Item, UItem, ListEditor, InstanceEditor, \
    EnumEditor, HGroup, VGroup, spring, Label, Spring
from src.envisage.tasks.base_editor import BaseTraitsEditor
from src.graph.graph import Graph
from src.constants import FIT_TYPES
from src.processing.tasks.analysis_edit.ianalysis_edit_tool import IAnalysisEditTool

#============= standard library imports ========================
from numpy import asarray, Inf
from src.graph.stacked_graph import StackedGraph
from src.graph.regression_graph import StackedRegressionGraph
from chaco.array_data_source import ArrayDataSource
#============= local library imports  ==========================
class Fit(HasTraits):
    name = Str
    use = Bool
    show = Bool
    fit = Str
    def traits_view(self):
        v = View(HGroup(
                        UItem('name', style='readonly'),
                        UItem('show'),
                        UItem('fit', editor=EnumEditor(values=FIT_TYPES),
                             enabled_when='show'
                             ),
                        UItem('use'),
                        )
                 )
        return v

class FitSelector(HasTraits):
    implements(IAnalysisEditTool)
    fits = List(Fit)
    update_needed = Event
    def traits_view(self):
        header = HGroup(
                        Spring(springy=False, width=50),
                        Label('Show'),
                        spring,
                        Label('Use'),
                        spring,
                        )
        v = View(
                 VGroup(
                        header,
                        Item('fits',
                             style='custom',
                             show_label=False,
                             editor=ListEditor(mutable=False,
                                            editor=InstanceEditor(),
                                            style='custom'
                                                )))
                 )
        return v

    @on_trait_change('fits:show')
    def _fit_changed(self):
        self.update_needed = True

    def load_fits(self, keys):
        self.fits = [
                     Fit(name=ki) for ki in keys
                    ]

    def _fits_default(self):
        return [Fit(name='Ar40')]

def normalize(xs, start=None):
    xs = asarray(xs)
    xs.sort()
    if start is None:
        start = xs[0]
    xs -= start

    # scale to hours
    xs = xs / (60.*60.)
    return xs

class BlanksEditor(BaseTraitsEditor):
    graph = Instance(Graph)
    name = Str
    tool = Instance(FitSelector, ())
    processor = Any

    unknowns = List
    references = List

    _unknowns = List
    _references = List

    def traits_view(self):
        v = View(UItem('graph', style='custom'))
        return v

    @on_trait_change('tool:update_needed')
    def _rebuild_graph(self):
        graph = self.graph
        graph.clear()
        uxs = [ui.timestamp for ui in self._unknowns]
        rxs = [ui.timestamp for ui in self._references]

        mrxs = min(rxs) if rxs else Inf
        muxs = min(uxs) if uxs else Inf

        start = min(mrxs, muxs)

        uxs = normalize(uxs, start)
        rxs = normalize(rxs, start)

        def get_isotope(ui, k, kind=None):
            if k in ui.isotopes:
                v = ui.isotopes[k]
                if kind is not None:
                    v = getattr(v, kind)
                v = v.value, v.error
            else:
                v = 0, 0
            return v

        refiso = self._unknowns[0]

        for i, ki in enumerate(refiso.isotope_keys):
            fit = next((fi for fi in self.tool.fits if fi.name == ki), None)
            if fit and fit.show:
                uys, ues = None, None
                if self._unknowns:
                    uys, ues = zip(*[get_isotope(ui, ki, 'blank')
                                for ui in self._unknowns
                                ])

                rys, res = None, None
                if self._references:
                    rys, res = zip(*[get_isotope(ui, ki)
                                for ui in self._references
                                ])

                p = graph.new_plot(
                                   ytitle=ki,
                                   xtitle='Time (hrs)',
                                   padding=[60, 10, 10, 60]
                                   )
                p.index_range.tight_bounds = False
                p.value_range.tight_bounds = False

                if ues and uys:
                    # plot unknowns
                    graph.new_series(uxs, uys,
                                     yerror=ArrayDataSource(ues),
                                     fit=False,
                                     type='scatter',
                                     plotid=i
                                     )

                if res and rys:
                    # plot references
                    graph.new_series(rxs, rys,
                                     yerror=ArrayDataSource(ues),
                                     type='scatter',
                                     plotid=i
                                     )

    @on_trait_change('unknowns[]')
    def _update_unknowns(self):

        graph = self.graph
        graph.clear()

        self._unknowns = self.processor.make_analyses(self.unknowns)
        self.processor.load_analyses(self._unknowns)

        '''
            TODO: find reference analyses using the current _unknowns
        '''

        self._rebuild_graph()

    @on_trait_change('references[]')
    def _update_references(self):

        graph = self.graph
        graph.clear()

        self._references = self.processor.make_analyses(self.references)
        self.processor.load_analyses(self._references)

        refiso = self._references[0]
        self.tool.load_fits(refiso.isotope_keys)
        self._rebuild_graph()

    def _graph_default(self):
        return StackedRegressionGraph(
                                      container_dict=dict(stack_order='top_to_bottom')
                                      )


#        g = Graph()
#        g.new_plot()
#        g.new_series([1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 2, 5])
#        return g
#============= EOF =============================================
