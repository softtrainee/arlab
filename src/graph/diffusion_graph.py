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
#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from graph import Graph


class DiffusionGraph(Graph):
    '''
    a graph for displaying diffusion data
    
    contains 4 plots 
    1. age-spectrum
    2.log r/ro
    3.arrhenius
    4.cooling histories
    
    '''
#    def __init__(self,*args,**kw):
#        super(DiffusionGraph,self).__init__(*args,**kw)
#        self.new_graph()
    bindings = None
    container_dict = dict(
    type='g',
    bgcolor='white',
    padding=[25, 5, 50, 30],
    spacing=(32, 25),
    shape=(2, 2))
    def show_plot_editor(self):
        '''
        '''

        i = self.selected_plotid
        names = ['Spectrum', 'LogR/Ro', 'Arrhenius', 'CoolingHistory']
        self._show_plot_editor(**{'name':names[i]})

    def set_group_binding(self, id, value):
        '''

        '''
        if self.bindings is None:
            self.bindings = []
        try:
            self.bindings[id] = value
        except IndexError:
            self.bindings.append(value)

    def update_group_attribute(self, plot, attr, value, dataid=0):
        '''

        '''
        
        if self.bindings[dataid]:
            index = None
            for k in self.groups:
                g = self.groups[k]
                for i, pp in enumerate(g):
                    
                    try:
                        index = pp.index(plot)
                        break
                    except ValueError:
                        continue

                if index is not None:
                    break

            if k == 'logr_ro':
                if not attr in ['line_width']:
                    g = self.groups['arrhenius']
                    g[i][index].trait_set(**{attr:value})

                g = self.groups['spectrum']
                if index % 2 == 0:
                    g[i][index].trait_set(**{attr:value})

            elif k == 'spectrum':
                if index % 2 == 0:
                    if not attr in ['line_width']:
                        g = self.groups['arrhenius']
                        g[i][index].trait_set(**{attr:value})

                    g = self.groups['logr_ro']
                    g[i][index].trait_set(**{attr:value})

            elif k == 'arrhenius':
                g = self.groups['logr_ro']
                g[i][index].trait_set(**{attr:value})

                g = self.groups['spectrum']
                if index % 2 == 0:
                    g[i][index].trait_set(**{attr:value})
            self.plotcontainer.invalidate_and_redraw()

    def new_graph(self):
        '''
        '''
        if self.groups:
            del(self.groups)
        self.groups = dict(spectrum=[],
                         logr_ro=[],
                         cooling_history=[],
                         arrhenius=[])

        for _i in range(4):
            self.new_plot(padding=5,
                          pan=True,
                          zoom=True)

#    def container_factory(self, *args, **kw):
#        '''
#            @type *args: C{str}
#            @param *args:
#
#            @type **kw: C{str}
#            @param **kw:
#        '''
#        return self._container_factory(
#                                       )
#    def set_group_color(self, gid=0, series=None):
#        '''
#            
#        '''
#        for k in ['spectrum', 'arrhenius', 'logr_ro', 'cooling_history']:
#            g = self.groups[k]
#            try:
#                plots = g[gid]
#                for p in plots:
#                    print p
#            except IndexError:
#                pass

    def set_group_visiblity(self, vis, gid=0):
        '''
          
        '''

        for k in ['spectrum', 'arrhenius', 'logr_ro', 'cooling_history']:
            g = self.groups[k]
            try:
                plots = g[gid]

                for p in plots:
                    p.visible = vis
            except IndexError:
                pass
        self.plotcontainer.invalidate_and_redraw()


    def build_spectrum(self, ar39, age, ar39_err, age_err, pid=0, **kw):
        '''

        '''

        a, _p = self.new_series(ar39_err, age_err, plotid=pid,
                        type='polygon',
                        color='orange')

        b, _p = self.new_series(ar39, age, plotid=pid, **kw)

        self.groups['spectrum'].append([b, a])

        self.set_x_title('Cum. 39Ar %', plotid=pid)
        self.set_y_title('Age (Ma)', plotid=pid)


    def build_logr_ro(self, ar39, logr, pid=1, ngroup=True, **kw):
        '''
        '''

        a, p = self.new_series(ar39, logr, plotid=pid, **kw)
        g = self.groups['logr_ro']
        if ngroup:
            g.append([a])
        else:
            #g[len(g) - 1].append(a)
            g[-1].append(a)

        self.set_x_title('Cum. 39Ar %', plotid=pid)
        self.set_y_title('Log R/Ro', plotid=pid)
        return a
    
    def build_arrhenius(self, T, Dta, pid=2, ngroup=True, **kw):
        '''
            
        '''

        a, _p = self.new_series(T, Dta, plotid=pid, type='scatter', marker_size=2.5, **kw)
        g = self.groups['arrhenius']
        if ngroup:
            g.append([a])
        else:
            #g[len(g) - 1].append(a)
            g[-1].append(a)

        self.set_x_title('10000/T (K)', plotid=pid)
        self.set_y_title('Log Dt/a^2', plotid=pid)

    def build_cooling_history(self, ts, Tsl, Tsh, pid=3):
        '''
                    '''
        self.set_x_title('t (Ma)', plotid=pid)
        self.set_y_title('Temp (C)', plotid=pid)
        self.set_y_limits(min=100, plotid=pid)
        a, _p = self.new_series(ts, Tsl, type='polygon', color=self.color_generators[pid].next())
        b, _p = self.new_series(ts, Tsh, type='polygon', color=self.color_generators[pid].next())

        self.groups['cooling_history'].append([a, b])



#============= views ===================================


#============= EOF ====================================
