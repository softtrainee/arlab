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



#============= enthought library imports =======================
from traits.api import HasTraits, Any, Instance
from traitsui.api import View, Item
from src.graph.graph import Graph

#============= standard library imports ========================

#============= local library imports  ==========================
from time_series_helper import parse_time_series_blob
from src.helpers.color_generators import colornames
from src.graph.regression_graph import RegressionGraph
class SummaryWindow(HasTraits):
    '''
        G{classtree}
    '''
    item = Any
    graph = Instance(Graph)
    def load(self):
        '''
        '''

        self.graph = RegressionGraph(container_dict=dict(type='g', shape=[2, 3],
                                       padding=0,
                                       fill_padding=True,
                                       spacing=(5, 5)
                                       ))
        if self.item is not None:
            for i, s in enumerate(self.item.signals):
                x, y = parse_time_series_blob(s.time_series)
                self.graph.new_plot(**dict(padding=[25, 0, 0, 25]))
                self.graph.new_series(x=x, y=y, plotid=i, color=colornames[i], type='scatter',
                                      marker_size=5, #1.75,
                                      marker='circle'
                                      )

#    def edit_traits(self, *args, **kw):
#        '''
#            @type *args: C{str}
#            @param *args:
#
#            @type **kw: C{str}
#            @param **kw:
#        '''
#        return super(SummaryWindow, self).edit_traits(*args, **kw)
    def traits_view(self):
        '''
        '''
        self.load()
        v = View(Item('graph', style='custom', show_label=False),
               resizable=True,
               width=500,
               height=500
               )
        return v
#============= views ===================================
#============= EOF ====================================
