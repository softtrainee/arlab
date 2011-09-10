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
from traits.api import  Instance, Event, Property, \
    DelegatesTo, Str
from traitsui.api import View, Item, HGroup, VGroup, \
    TableEditor, InstanceEditor, Handler
from traitsui.table_column import ObjectColumn
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.managers.manager import Manager
from src.scripts.laser.power_map_script import PowerMapScript
#class PowerMapStep(HasTraits):
#    beam_diameter = Float
#    padding = Float
#    step_length = Float
#    power = Float
class PowerMapHandler(Handler):
    def close(self, info, ok):
        info.object.script.kill_script()
        return True

class PowerMapManager(Manager):

    script = Instance(PowerMapScript)
    steps = DelegatesTo('script')
    file_name = Str

    start_button = Event

    start_label = Property(depends_on='script._alive')

    def _get_start_label(self):
        return 'Stop' if self.script.isAlive() else 'Start'

    def _file_name_changed(self):

        root, tail = os.path.split(self.file_name)
        self.script.source_dir = root
        self.script.file_name = tail
        self.title = tail
        self.script.load_steps()


    def _start_button_fired(self):
        if not self.script.isAlive():
            self.script.bootstrap()
        else:
            self.script.kill_script()

    def new_script(self):

        root, name = os.path.split(self.file_name)
        self.script = PowerMapScript(
                              source_dir=root,
                              file_name=name,
                              manager=self.parent)
        self.script.load_steps()

    def _script_default(self):
        return PowerMapScript()

    def traits_view(self):
        cols = [
              ObjectColumn(name='beam_diameter'),
              ObjectColumn(name='padding'),
              ObjectColumn(name='step_length'),
              ObjectColumn(name='power'),
              ObjectColumn(name='est_duration', editable=False)

              ]
        v = View(
                 VGroup(
                         self._button_factory('start_button', 'start_label', None, align='right'),
                         HGroup(

                                Item('steps', width=0.32, show_label=False, editor=TableEditor(columns=cols,
                                                                                       selected='object.script.selected'
                                                                                       )),
                                Item('script', width=0.68, show_label=False, style='custom', editor=InstanceEditor(view='canvas_view'))
                                )
                        ),
                title=self.title,
                handler=PowerMapHandler,
                resizable=True,
                width=890,
                height=650
                )
        return v

#============= views ===================================
#============= EOF ====================================
