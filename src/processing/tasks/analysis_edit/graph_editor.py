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
from traits.api import Any, List, on_trait_change, Instance, Property, Event, File
from traitsui.api import View, UItem, InstanceEditor
from src.envisage.tasks.base_editor import BaseTraitsEditor
#============= standard library imports ========================
from numpy import asarray
from src.processing.tasks.analysis_edit.fits import FitSelector
from src.helpers.isotope_utils import sort_isotopes
from src.graph.regression_graph import StackedRegressionGraph
import os
import copy
from itertools import groupby
from src.helpers.iterfuncs import partition
from numpy.ma.core import ids
#============= local library imports  ==========================


class GraphEditor(BaseTraitsEditor):
    tool = Instance(FitSelector, ())
    graph = Any
    processor = Any
    unknowns = List
    _unknowns = List
    component = Property
    _component = Any

    component_changed = Event
    path = File
    analysis_cache = List

    def normalize(self, xs, start=None):
        xs = asarray(xs)
        xs.sort()
        if start is None:
            start = xs[0]
        xs -= start

        # scale to hours
        xs = xs / (60.*60.)
        return xs

    @on_trait_change('unknowns[]')
    def _update_unknowns(self):

        '''
            TODO: find reference analyses using the current _unknowns
        '''
        self._unknowns = self._gather_unknowns(True)

#         self._make_unknowns()
        self.rebuild_graph()

        keys = set([ki  for ui in self._unknowns
                            for ki in ui.isotope_keys])
        keys = sort_isotopes(keys)

        refiso = self._unknowns[0]

        self.tool.load_fits(refiso.isotope_keys,
                            refiso.isotope_fits
                            )

        self._update_unknowns_hook()

    def _update_unknowns_hook(self):
        pass

    @on_trait_change('tool:update_needed')
    def _tool_refresh(self):
        self.rebuild_graph()
        if not self.tool.suppress_refresh_unknowns:
            self.refresh_unknowns()


    def refresh_unknowns(self):
        pass

    def rebuild_graph(self):
        graph = self.graph
        graph.clear()
        self._rebuild_graph()
#         graph.refresh()

        self.component_changed = True

    def _rebuild_graph(self):
        pass

#     def _make_unknowns(self):
#         if self.unknowns:
#             self._unknowns = self.processor.make_analyses(self.unknowns)
# #             self.processor.load_analyses(self._unknowns)

    def traits_view(self):
        v = View(UItem('graph',
                       style='custom',
                       editor=InstanceEditor()))
        return v

    def _graph_default(self):
        return self._graph_factory()

    def _graph_factory(self):
        g = StackedRegressionGraph(container_dict=dict(stack_order='top_to_bottom'))
        return g

    def _graph_generator(self):
        for fit in self.tool.fits:
            if fit.fit and fit.show:
                yield fit

    def _get_component(self):
        return self.graph.plotcontainer

    def save_file(self, path):
        _, tail = os.path.splitext(path)
        if tail not in ('.pdf', '.png'):
            path = '{}.pdf'.format(path)

        c = self.component

        '''
            chaco becomes less responsive after saving if 
            use_backbuffer is false and using pdf 
        '''
        c.use_backbuffer = True

        _, tail = os.path.splitext(path)
        if tail == '.pdf':
            from chaco.pdf_graphics_context import PdfPlotGraphicsContext
            gc = PdfPlotGraphicsContext(filename=path,
#                                         pagesize='letter'
                                        )
            gc.render_component(c, valign='center')
            gc.save()
        else:
            from chaco.plot_graphics_context import PlotGraphicsContext
            gc = PlotGraphicsContext((int(c.outer_width), int(c.outer_height)))
            gc.render_component(c)
            gc.save(path)

#         with gc:
#         self.rebuild_graph()

    def _gather_unknowns(self, refresh_data):

        ans = self._unknowns
        if refresh_data or not ans:
            ids = [ai.uuid for ai in self.analysis_cache]
            aa = [ai for ai in self.unknowns if ai.uuid not in ids]

            nids = (ai.uuid for ai in self.unknowns if ai.uuid in ids)
            bb = [next((ai for ai in self.analysis_cache if ai.uuid == i)) for i in nids]
            aa = list(aa)
            if aa:
                unks = self.processor.make_analyses(list(aa))
                ans = unks
                if bb:
                    ans.extend(bb)
            else:
                ans = bb

            # compress groups
            self._compress_unknowns(ans)
            self._unknowns = ans

        return ans

    def _compress_unknowns(self, ans):
        key = lambda x: x.group_id
        ans = sorted(ans, key=key)
        groups = groupby(ans, key)

        mgid, analyses = groups.next()
        for ai in analyses:
            ai.group_id = 0

        for gid, analyses in groups:
            for ai in analyses:
                ai.group_id = gid - mgid
#============= EOF =============================================
