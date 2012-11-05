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

#=============standard library imports ========================

#=============local library imports  ==========================
from graph import Graph
from chaco.plot import Plot
from chaco.scatterplot import ScatterPlot


class StackedGraph(Graph):
    '''
    '''
    equi_stack = True
    panel_height = 100
    _has_title = False
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
        bottom = self.plotcontainer.stack_order == 'bottom_to_top'
        if self.equi_stack:
            kw['resizable'] = 'h'
            if 'bounds' not in kw:
                kw['bounds'] = (1, self.panel_height)
#
        n = len(self.plotcontainer.components)
#        print n
        if 'title' in kw:
            self._has_title = True

        if n > 0:
#            key = 'padding_top'
#            if 'title' not in kw:
#                kw['padding_top'] = 


#        else:
            kw['resizable'] = 'h'
            if 'bounds' not in kw:
                kw['bounds'] = (1, self.panel_height)

#            if bottom:
#                kw['padding_bottom'] = 0
#                if 'title' not in kw:
#                    kw['padding_top'] = 20
#                else:
#                    kw['padding_top'] = 30
#            else:
#                kw['padding_bottom'] = 30
#                kw['padding_top'] = 0
#        print kw

        p = super(StackedGraph, self).new_plot(**kw)
        p.value_axis.ensure_labels_bounded = True

        if n > 1:
#            if not bottom:
##                plotiter = self.plots[1:]
#                plotiter1 = self.plots[:-1]
#            else:
##                plotiter = self.plots[:-1]
#                plotiter1 = self.plots[1:]

#            pm = self.plots[0]
            pm = self.plotcontainer.components[0]
            pind = pm.index_range
            for pi in self.plotcontainer.components[1:]:
                pi.index_range = pind

#            link = True
#            if 'link' in kw:
#                link = kw['link']
#
#            if link:
#                pm = self.plots[0].index_mapper
##                pii = self.plots[0].index_axis
##                for pi in self.plots[1:]:
##                    pi.index_mapper = pm
##                    pi.index_axis = pii
##                print pi, link, self.plots[0]
###                pi.padding_top = 0
###                pi.padding_bottom = 0
#                if link:
###                    pi.index_range = self.plots[0].index_range
#                    p.index_mapper = self.plots[0].index_mapper
#            for pi in plotiter1:
#                pi.index_axis.visible = False
#                pi.padding_top = 0
#                pi.padding_bottom = 0
        self.set_paddings()

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
                pi.padding_bottom = 50

                pi.padding_top = pt
                pi.index_axis.visible = True
            else:
                pi.padding_top = 0
                if i == 0:
                    pi.padding_bottom = 50
                    pi.index_axis.visible = True
                else:
                    pi.padding_bottom = 0
                    pi.index_axis.visible = False
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
        s, _p = super(StackedGraph, self).new_series(*args, **kw)
        self._bind_index(s.index)
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

    def _update_metadata(self, obj, name, old, new):
        for plot in self.plots:
            for ps in plot.plots.itervalues():
                si = ps[0]
                if isinstance(si, ScatterPlot):
                    if not si.index is obj:
                        si.index.trait_set(metadata=obj.metadata)
                        si.value.trait_set(metadata=obj.metadata)


    def _bind_index(self, index, bind_selection=True, **kw):
        if bind_selection:
            index.on_trait_change(self._update_metadata, 'metadata_changed')

#============= EOF ====================================
