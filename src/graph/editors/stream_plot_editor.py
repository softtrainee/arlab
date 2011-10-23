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
'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#=============enthought library imports=======================
from traits.api import DelegatesTo, Property, Float
from traitsui.api import Item, VGroup
#=============standard library imports ========================

#=============local library imports  ==========================
from src.graph.editors.plot_editor import PlotEditor
class StreamPlotEditor(PlotEditor):
    '''
    '''
    track_x = DelegatesTo('graph')
    track_y = DelegatesTo('graph')
    
    
    data_limit = Property(Float(enter_set=True, auto_set=False),
                          depends_on='_data_limit')
    _data_limit = Float

    def __init__(self, *args, **kw):
        '''

        '''
        super(PlotEditor, self).__init__(*args, **kw)
        if self.graph:
            self._data_limit = self.graph.data_limits[self.id]
            self._build_series_editors()
            
            self.plot.index_mapper.on_trait_change(self.update_x, 'updated')
            self.plot.value_mapper.on_trait_change(self.update_y, 'updated')

    def update_x(self, o, oo, nn):
        '''
        '''
        if not isinstance(nn, bool) and self.track_x:
            self._xmax = nn.high
            self._xmin = nn.low

    def update_y(self, o, n, nn):
        '''
        '''
        if not isinstance(nn, bool) and self.track_y:
            self._ymax = nn.high
            self._ymin = nn.low
            
    def _track_x_changed(self):    
        if not self.track_x:
            self.graph.track_x = False
            self.graph.set_x_limits(min=self._xmin, max=self._xmax, plotid=self.id)
        else:
            self.graph.track_x = True
    
    def _track_y_changed(self):    
        if not self.track_y:
            self.graph.track_y = False
            self.graph.set_y_limits(min=self._ymin, max=self._ymax, plotid=self.id)
        else:
            self.graph.track_y = True
    
    def get_axes_group(self):
        grp = super(StreamPlotEditor, self).get_axes_group()
        agrp = VGroup(Item('track_x'), Item('data_limit'))
        grp.content.insert(0, agrp)
        grp.content.insert(2, Item('track_y'))
        return grp

    def _get_data_limit(self):
        return self._data_limit

    def _set_data_limit(self, v):
        self._data_limit = v
        self.graph.data_limits[self.id] = v
        self.graph.force_track_x_flag = True
        
    def _validate_data_limit(self, v):
        try:
            return float(v)
        except ValueError:
            pass
#============= EOF ====================================


