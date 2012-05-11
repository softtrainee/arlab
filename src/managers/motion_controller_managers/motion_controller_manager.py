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
from traits.api import Instance, Enum, DelegatesTo, Property, Button, Any
from traitsui.api import View, Item, HGroup, spring, \
    ListEditor
#=============standard library imports ========================

#=============local library imports  ==========================
from src.managers.manager import Manager
#from src.hardware.newport.newport_motion_controller import NewportMotionController
from src.hardware.motion_controller import MotionController
from src.helpers.paths import root_dir, device_dir
from src.helpers.filetools import parse_file
import os

#class MotionControllerManagerHandler(Handler):
#    def closed(self, info, is_ok):
#        '''
#           
#        '''
#        info.object.motion_controller.save_parameters()
#        Handler.closed(self, info, is_ok)

class MotionControllerManager(Manager):
    '''
    '''

    motion_controller = Instance(MotionController)
    _axes = DelegatesTo('motion_controller', prefix='axes')
    axes = Property

    apply_button = Button('Apply')
    read_button = Button('Read')
    load_button = Button('Load')
    motion_group = DelegatesTo('motion_controller', prefix='groupobj')

    view_style = Enum('simple_view', 'full_view')

    selected = Any
    def kill(self, **kw):
        super(MotionControllerManager, self).kill(**kw)
        self.motion_controller.save_axes_parameters()

    def _load_button_fired(self):
        path = self.open_file_dialog(default_directory=device_dir)
        #path = os.path.join(root_dir, 'zobs', 'NewStage-Axis-1.txt')
        if path is not None:


            #sniff the file to get the axis
            lines = parse_file(path)

            aid = lines[0][0]
            try:
                ax = self._get_axis_by_id(aid)
                func = ax.load_parameters_from_file
            except ValueError:
                #this is a txt file not a cfg 
                ax = self._get_selected()
                if ax is not None:
                    func = ax.load


            if ax is not None:
                func(path)
                #ax.load_parameters_from_file(path)
                #ax.load_parameters_from_file(path)

    def _get_axis_by_id(self, aid):
        return next((a for a in self._axes.itervalues() if a.id == int(aid)), None)

    def _get_axes(self):
        '''
        '''
        keys = self._axes.keys()
        keys.sort()

        return [self._axes[k] for k in keys] + [self.motion_group]

#    def _restore_fired(self):
#        '''
#        '''
#        self.motion_controller.axes_factory()
#        self.trait_property_changed('axes', None)
#        for a in self.axes:
#            a.load_

#    def _apply_all_fired(self):
#        '''
#        '''
##        for a in self.axes:
##            a.upload_parameters_to_device()
#        if sele
##        self.motion_controller.save()
    def _get_selected(self):
        ax = self.selected
        if ax is None:
            ax = self.axes[0]

        return ax

    def _read_button_fired(self):
        ax = self._get_selected()
        ax._read_parameters_fired()

    def _apply_button_fired(self):
        ax = self._get_selected()

        if ax is not None:
            ax.upload_parameters_to_device()

        self.motion_controller.save_axes_parameters(axis=ax)

    def configure_view(self):
        v = View(Item('axes',
                       style='custom',
                       show_label=False,
                       editor=ListEditor(use_notebook=True,
                                                dock_style='tab',
                                                page_name='.name',
                                                view=self.view_style,
                                                selected='selected'
                        )
                        ),
                    HGroup(spring, Item('load_button'), Item('read_button'), Item('apply_button'), show_labels=False,
#                           visible_when='view_style=="full_view"'
                           ),
                #resizable=True,
                #handler=self.handler_klass, #MotionControllerManagerHandler,
                #title='Configure Motion Controller'
                )
        return v

    def traits_view(self):
        '''
        '''
        view = View(Item('axes',
                       style='custom',
                       show_label=False,
                       editor=ListEditor(use_notebook=True,
                                                dock_style='tab',
                                                page_name='.name',
                                                view=self.view_style
                        )
                        ),
                    HGroup(spring, Item('load_button'), Item('restore'), Item('apply_button'), show_labels=False,
                           #visible_when='view_style=="full_view"'
                           ),
                resizable=True,
                handler=self.handler_klass, #MotionControllerManagerHandler,
                title='Configure Motion Controller'
                )
        return view
