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


class StackedGraph(Graph):
    '''
    '''
    equi_stack = True
    panel_height = 100

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
        c.on_trait_change(self._bounds_changed_, 'bounds')
        return c

    def new_plot(self, **kw):
        '''
        '''

        if self.equi_stack:
            kw['resizable'] = 'h'
            if 'bounds' not in kw:
                kw['bounds'] = (50, self.panel_height)
#
        if len(self.plots) == 0:
            if 'title' not in kw:
                kw['padding_top'] = 0
#
        else:
            kw['resizable'] = 'h'
            if 'bounds' not in kw:
                kw['bounds'] = (50, self.panel_height)

            kw['padding_bottom'] = 0
            if 'title' not in kw:
                kw['padding_top'] = 20
            else:
                kw['padding_top'] = 30

        p = super(StackedGraph, self).new_plot(**kw)
        p.value_axis.ensure_labels_bounded = True

        for p in self.plots[1:]:
            p.padding_top = 0
            p.padding_bottom = 0

        link = True
        if 'link' in kw:
            link = kw['link']

        if len(self.plots) > 1 and link:
            for p in self.plots[1:]:
                p.index_axis.visible = False
                p.index_range = self.plots[0].index_range

    def _bounds_changed_(self, bounds):
        '''
            vertically resizes the stacked graph.
            the plots are sized equally
        '''
        padding_top = sum([getattr(p, 'padding_top') for p in self.plots])
        padding_bottom = sum([getattr(p, 'padding_bottom') for p in self.plots])

        pt = self.plotcontainer.padding_top + \
                self.plotcontainer.padding_bottom + \
                    padding_top + padding_bottom
        if self.equi_stack:
            for p in self.plots:
                p.bounds[1] = (bounds[1] - pt) / len(self.plots)
        else:
            self.plots[0].bounds[1] = (bounds[1] - pt) / max(1, (len(self.plots) - 1))
#============= EOF ====================================
