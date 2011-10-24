'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#=============enthought library imports=======================

#=============standard library imports ========================

#=============local library imports  ==========================
from graph import Graph
class StackedGraph(Graph):
    '''
    '''
    equi_stack = True
    panel_height = 100
    def new_plot(self, **kw):
        '''
        '''
        if self.equi_stack:
            kw['resizable'] = 'h'
            if 'bounds' not in kw:
                kw['bounds'] = (50, self.panel_height)

        if len(self.plots) == 0:
            if 'title' not in kw:
                kw['padding_top'] = 0

        else:
            kw['resizable'] = 'h'
            if 'bounds' not in kw:
                kw['bounds'] = (50, self.panel_height)

            if 'title' not in kw:
                kw['padding_top'] = 20
                kw['padding_bottom'] = 0
            else:
                kw['padding_top'] = 30
                kw['padding_bottom'] = 0

        p = super(StackedGraph, self).new_plot(**kw)
        p.value_axis.ensure_labels_bounded = True
        for p in self.plots[1:-1]:
            p.padding_top = 0
            p.padding_bottom = 0
#        for p in self.plots:
#            p.height = 60

        link = True
        if 'link' in kw:
            link = kw['link']
            
        if len(self.plots) > 1 and link:
            for p in self.plots[1:]:
                p.index_axis.visible = False
                p.index_range = self.plots[0].index_range
                
#============= EOF ====================================
