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
from traits.api import HasTraits, on_trait_change, \
    Instance, Bool, Int, Any, Property, Str
from traitsui.api import View, Item, VGroup, ColorEditor, EnumEditor
from chaco.api import BaseXYPlot
#=============standard library imports ========================
from wx import Colour
from chaco.default_colormaps import color_map_name_dict
from chaco.base_2d_plot import Base2DPlot
#from chaco.contour_poly_plot import ContourPolyPlot
from chaco.data_range_1d import DataRange1D

#=============local library imports  ==========================

class SeriesEditor(HasTraits):
    name = Property(depends_on='_name')
    _name = Str

    plotid = Int
    id = Int
    graph = Any
    series = Instance(BaseXYPlot)

    show = Bool(True)
    def _get_name(self):
        if not self._name:
            return 'series{:03d}'.format(self.id)
        return self._name

    def _set_name(self, v):
        self._name = v

    @on_trait_change('series.+')
    def _series_changed(self, obj, name, new):
        '''
        '''
        if name[0] != '_' and name[-1:] != '_' and name not in ['visible', 'series']:
            self.graph.update_group_attribute(obj, name, new, dataid=self.id / 2)

    def _show_changed(self, name, old, new):
        '''
        '''
        self.graph.set_series_visiblity(new, plotid=self.plotid,
                                        series=self.id)

    def traits_view(self):
        '''
        '''

        return View(VGroup(
                            Item('name', show_label=False),
                            Item('series', style='custom', show_label=False)
                           )
                    )
class ContourPolyPlotEditor(SeriesEditor):
#    series=Instance(ContourPolyPlot)
    series=Instance(Base2DPlot)
    series2=Instance(Base2DPlot)
    cmap=Str('yarg')
    def __init__(self, *args,**kw):
        super(ContourPolyPlotEditor,self).__init__(*args,**kw)
        self.cmap_names=color_map_name_dict.keys()
    
    def _cmap_changed(self):
        
        r=self.series.value.get_bounds()
        func=color_map_name_dict[self.cmap]
        cm=func(DataRange1D(low_setting=0,high_setting=r[1]))
        for p in self.graph.plots[self.plotid].plots.itervalues():
            p=p[0]
            p.color_mapper=cm
            p.bgcolor=cm.color_bands[0]

        self.series.invalidate_and_redraw()
        
    def traits_view(self):
        '''
        '''
        v = View(VGroup(
                      Item('show', label='hide/show'),
                      Item('cmap', editor=EnumEditor(name='cmap_names')
                           )
                      )
                )
        return v
    
class PolygonPlotEditor(SeriesEditor):
    #series = Instance(BaseXYPlot)

    color_ = Property
    def _get_color_(self):
        '''
        '''
        if isinstance(self.series.face_color, str):
            c = Colour()
            c.SetFromName(self.series.face_color)
        else:
            c = self.series.face_color
        return c

    def _set_color_(self, c):
        '''
        '''

        self.series.face_color = c
        self.series.edge_color = c
        self.series.request_redraw()


    def traits_view(self):
        '''
        '''
        v = View(VGroup(
                      Item('show', label='hide/show'),
                      Item('color_', style='custom', editor=ColorEditor())
                      )
                )
        return v
#================= EOF ==============================================
