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
from traits.api import HasTraits, Bool, Property, Str, Any, on_trait_change
from wx import Color, ColourDatabase

#============= standard library imports ========================
import os
#============= local library imports  ==========================

#============= views ===================================
class ModelDataDirectory(HasTraits):
    '''
    '''
    show = Bool
    bind = Bool
    name = Property(depends_on='path')
    path = Str
    id = 0
    modeler = Any
    primary_color = Str#Color
    secondary_color = Str#Color
    
    model_spectrum_enabled = Bool
    model_arrhenius_enabled = Bool
    
    def _get_name(self):
        '''
        '''
        return os.path.basename(self.path)

    def _show_changed(self):
        '''
        '''
        if self.modeler:
            self.modeler.graph.set_group_visiblity(self.show, gid=self.id)
            self.model_arrhenius_enabled = self.show
            self.model_spectrum_enabled = self.show
            self.modeler.update_graph_title()
            
    def _model_arrhenius_enabled_changed(self):
        if self.modeler:
            try:
                p = self.modeler.graph.groups['arrhenius'][self.id][1]
                self.modeler.graph.set_plot_visibility(p, self.model_arrhenius_enabled)
            except IndexError:
                #this group does not have a model arrhenius
                pass
            try:
                p = self.modeler.graph.groups['logr_ro'][self.id][1]
                self.modeler.graph.set_plot_visibility(p, self.model_arrhenius_enabled)
            except IndexError, KeyError:
                #this group does not have a model logr_ro
                pass
            
    def _model_spectrum_enabled_changed(self):
        if self.modeler:
            try:
                p = self.modeler.graph.groups['spectrum'][self.id][2]
                self.modeler.graph.set_plot_visibility(p, self.model_spectrum_enabled)
            except IndexError:
                #this group does not have a model spectrum
                pass
            
    def _bind_changed(self):
        '''
        '''
        if self.modeler:
            self.modeler.graph.set_group_binding(self.id, self.bind)
            
    def update_pcolor(self, new):
        new = [255 * i for i in new[:2]]
        c = Color(*new)
        self.primary_color = ColourDatabase().FindName(c).lower()
        
    def update_scolor(self, new):
        new = [255 * i for i in new]
        c = Color(*new)
        self.secondary_color = ColourDatabase().FindName(c).lower()

#    @on_trait_change('primary_color, secondary_color')
#    def _color_changed(self):
#        
#        
#        try:
#            for k, v in self.modeler.graph.groups.iteritems():
#                if k in ['spectrum', 'logr_ro', 'arrhenius', ]: 
#                    v[self.id][0].color = self.primary_color
#                    v[self.id][1].color = self.secondary_color
#                elif k == 'cooling_history':
#                    v[self.id][0].face_color = self.primary_color 
#                    v[self.id][0].edge_color = self.primary_color 
#                    
#                    v[self.id][1].face_color = self.secondary_color 
#                    v[self.id][1].edge_color = self.secondary_color 
#                    
#        except Exception, err:
#            print err
#============= EOF ====================================
