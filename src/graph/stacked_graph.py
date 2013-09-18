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
from traits.api import Bool
from chaco.scatterplot import ScatterPlot
#=============standard library imports ========================

#=============local library imports  ==========================
from graph import Graph


class StackedGraph(Graph):
    '''
    '''
    bind_index = Bool(True)
    equi_stack = True
    panel_height = 100
    _has_title = False
    padding_bottom = 50

    def add_minor_xticks(self, plotid=0, **kw):
        if plotid != 0:
            kw['aux_component'] = self.plots[0]

        super(StackedGraph, self).add_minor_xticks(plotid=plotid, **kw)

    def add_minor_yticks(self, plotid=0, **kw):
        if plotid != 0:
            kw['aux_component'] = self.plots[0]

        super(StackedGraph, self).add_minor_yticks(plotid=plotid, **kw)

    def container_factory(self, *args, **kw):
        c = super(StackedGraph, self).container_factory(*args, **kw)
        '''
            bind to self.plotcontainer.bounds
            allows stacked graph to resize vertically
        '''
        c.on_trait_change(self._bounds_changed, 'bounds')
        return c

    def new_plot(self, **kw):
        '''
        '''
#        self.plotcontainer.stack_order = 'bottom_to_top'
#        bottom = self.plotcontainer.stack_order == 'bottom_to_top'
#        if self.equi_stack:
#            kw['resizable'] = 'h'
#            if 'bounds' not in kw:
#                kw['bounds'] = (1, self.panel_height)
#
        n = len(self.plotcontainer.components)
#        print n
        if 'title' in kw:
            if self._has_title:
                kw.pop('title')
            self._has_title = True

        if n > 0:
            kw['resizable'] = 'h'
            if 'bounds' not in kw:
                kw['bounds'] = (1, self.panel_height)

        p = super(StackedGraph, self).new_plot(**kw)
        p.value_axis.ensure_labels_bounded = True

        if n >= 1:
            pm = self.plotcontainer.components[0]
            pind = pm.index_range
            for pi in self.plotcontainer.components[1:]:
                pi.index_range = pind

        self.set_paddings()
        self._bounds_changed(self.plotcontainer.bounds)
#        p.border_visible = False
        return p

    def set_paddings(self):
        pc = self.plotcontainer
        n = len(pc.components)
        bottom = pc.stack_order == 'bottom_to_top'
        comps = pc.components
        if not bottom:
            comps = reversed(comps)

        pt = 20 if self._has_title else 10
        for i, pi in enumerate(comps):
            if n == 1:
                pi.padding_bottom = self.padding_bottom

                pi.padding_top = pt
                pi.index_axis.visible = True

            else:
                pi.padding_top = 0
                if i == 0:
                    pi.padding_bottom = self.padding_bottom
                    pi.index_axis.visible = True
                else:
                    pi.index_axis.visible = False
                    pi.padding_bottom = 0
                    if i == n - 1:
                        pi.padding_top = pt

#        else:
#            for i, pi in enumerate(pc.components):
#                if n == 1:
#                    pi.padding_bottom = 50
#                    pi.padding_top = 10
#                    pi.index_axis.visible = True
#                else:
#                    pi.padding_top = 0
#                    if i == 0:
#                        pi.padding_bottom = 50
#                        pi.index_axis.visible = True
#                    else:
#                        pi.padding_bottom = 0
#                        pi.index_axis.visible = False
#                        if i == n - 1:
#                            pi.padding_top = 10
#        a = n - 1 if bottom else 0
#        for i, pi in enumerate(pc.components):
#            if i == a:
#                pi.padding_bottom = 50
#                pi.padding_top = 10
#                pi.index_axis.visible = True
#            else:
#                pi.index_axis.visible = False
#                pi.padding_top = 0
#                pi.padding_bottom = 0

    def new_series(self, *args, **kw):
        if not 'plotid' in kw:
            kw['plotid'] = 0

        plotid = kw['plotid']
        s, _p = super(StackedGraph, self).new_series(*args, **kw)

        series_id = self.series[plotid][-1]
#        print series_id
        self._bind_index(s, series_id)
        return s, _p

    def _bounds_changed(self, bounds):
        '''
            vertically resizes the stacked graph.
            the plots are sized equally
        '''
        self._update_bounds(bounds, self.plotcontainer.components)

    def _update_bounds(self, bounds, comps):

        padding_top = sum([getattr(p, 'padding_top') for p in comps])
        padding_bottom = sum([getattr(p, 'padding_bottom') for p in comps])
#
        pt = self.plotcontainer.padding_top + \
                self.plotcontainer.padding_bottom + \
                    padding_top + padding_bottom
#        pt = 60
        n = len(self.plotcontainer.components)
        if self.equi_stack:
            for p in self.plotcontainer.components:
                p.bounds[1] = (bounds[1] - pt) / n
        else:
            try:
                self.plots[0].bounds[1] = (bounds[1] - pt) / max(1, (n - 1))
            except IndexError:
                pass

    def _update_metadata(self, scatter, series_id, obj, name, old, new):
        for plot in self.plots:
            for k, ps in plot.plots.iteritems():
                si = ps[0]
                sii = int(series_id[0][-1])
                try:
                    pi = int(k[-1])
#                    if isinstance(si, ScatterPlot):
                    if not si.index is obj and pi == sii:
                        si.index.trait_set(metadata=obj.metadata)
                except ValueError:
                    pass
    def _bind_index(self, scatter, series_id, bind_selection=True, **kw):
        if bind_selection:
            u = lambda obj, name, old, new: self._update_metadata(scatter, series_id, obj, name, old, new)
            scatter.index.on_trait_change(u, 'metadata_changed')
#        pass
#============= EOF ====================================
