#=============enthought library imports=======================

#=============standard library imports ========================

#=============local library imports  ==========================
from graph import Graph
class StackedGraph(Graph):
    '''
    '''
    equi_stack = True
    def new_plot(self, **kw):
        '''
        '''
        if self.equi_stack:
            kw['resizable'] = 'h'
            if 'bounds' not in kw:
                kw['bounds'] = (50, 100)

        if len(self.plots) == 0:
            if 'title' not in kw:
                kw['padding_top'] = 0

        else:
            kw['resizable'] = 'h'
            if 'bounds' not in kw:
                kw['bounds'] = (50, 100)

            if 'title' not in kw:
                kw['padding_top'] = 20
                kw['padding_bottom'] = 0
            else:
                kw['padding_top'] = 30
                kw['padding_bottom'] = 0

        p = super(StackedGraph, self).new_plot(**kw)
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
