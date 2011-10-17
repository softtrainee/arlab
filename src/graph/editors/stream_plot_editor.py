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
from traitsui.api import Item, HGroup
#=============standard library imports ========================

#=============local library imports  ==========================
from src.graph.editors.plot_editor import PlotEditor
class StreamPlotEditor(PlotEditor):
    '''
        G{classtree}
    '''
    autoupdate = DelegatesTo('graph')
    data_limit = Property(Float(enter_set=True, auto_set=False),
                          depends_on='_data_limit')
    _data_limit = Float

    def __init__(self, *args, **kw):
        '''
            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        super(PlotEditor, self).__init__(*args, **kw)
        if self.graph:
            self._data_limit = self.graph.data_limits[self.id]
            self._build_series_editors()
#

    def _autoupdate_changed(self):
        '''
        '''
        if not self.autoupdate:
            self.graph.set_x_limits(min=self._xmin, max=self._xmax, plotid=self.id)
            self.graph.set_y_limits(min=self._ymin, max=self._ymax, plotid=self.id)
            self.graph.auto_update(False, plotid=self.id)
            #self.graph.trim_data[self.id]=False
        else:

            self.graph.auto_update(True, plotid=self.id)

    def get_axes_group(self):
        #grp = super(StreamPlotEditor, self).get_axes_group()
        grp = PlotEditor.get_axes_group(self)
        agrp = HGroup(Item('autoupdate'), Item('data_limit'))
        grp.content.insert(0, agrp)
        return grp

    def _get_data_limit(self):
        return self._data_limit

    def _set_data_limit(self, v):
        self.graph.data_limits[self.id] = float(v)
        self.graph.update_x_limits[self.id] = True
        self._data_limit = v
#============= EOF ====================================


