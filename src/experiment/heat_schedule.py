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
from traits.api import on_trait_change, HasTraits, Instance, List, \
     Enum, Str, Float, Button, Property, Event, Any, CFloat
import apptools.sweet_pickle as pickle
from traitsui.api import View, Item, HGroup, Spring, spring, VGroup, TabularEditor
from traitsui.tabular_adapter import TabularAdapter
#from traitsui.editors.tabular_editor import TabularEditor
from pyface.api import FileDialog, OK
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.helpers.filetools import parse_file
from src.paths import paths


class HeatStepAdapter(TabularAdapter):
    can_drop = True
    kind = Str

    state_image = Property
    state_text = Property
    state_width = Property
    def set_kind(self, kind):
        self.kind = kind
        self.columns = self._columns_factory()
    def _columns_default(self):
        return self._columns_factory()
    def _columns_factory(self):
        hp = ('Temp', 'extract_value')

        if self.kind == 'power':
            hp = ('Power', 'extract_value')

        return [
                #('', 'step'), 
                ('', 'state'), hp ,
                ('Duration (sec)', 'duration'),
                ]

#    def insert(self, object, name, row, item):
#        print object, name, row, item
#        object.steps.insert(row - 1, HeatStep())

    def get_width(self, object, trait, column):
        w = -1
        if column == 0:
            w = 20
#        elif column == 1:
#            w = 20
        return w

    def get_can_edit(self, obj, name, row):
        edit = True

        if getattr(obj, name)[row].state in ['success', 'fail']:
            edit = False
        return edit

#    def get_default_value(self, obj, name):
#        print obj, name

    def _get_state_text(self):
        return ''

    def _set_state_text(self, v):
        pass

    def get_format(self, obj, name, row, column):
        if column == 3: #elapsed_time
            fmt = '%0.3f'
        else:
            fmt = '%s'

        return fmt

    def _get_state_image(self):
        if self.item:
            im = 'gray'

            if self.item.state == 'running':
                im = 'orange'
            elif self.item.state == 'success':
                im = 'green'
            elif self.item.state == 'fail':
                im = 'red'

            #get the source path
            root = os.path.split(__file__)[0]
            while not root.endswith('src'):
                root = os.path.split(root)[0]
            root = os.path.split(root)[0]
            root = os.path.join(root, 'resources')
            return os.path.join(root, '{}_ball.png'.format(im))

class HeatStep(HasTraits):
    extract_value = Property
    _power = Float

    duration = Property
    _duration = Float

#    elapsed_time = CFloat
    state = Enum('not run', 'running', 'success', 'fail')
    step = Str
#    update = Event

    def _get_extract_value(self):
        return self._power

    def _validate_extract_value(self, v):
        return self._validate_float(v, self._power)

    def _set_extract_value(self, v):
        self._power = v

    def _get_duration(self):
        return self._duration

    def _validate_duration(self, v):
        return self._validate_float(v, self._duration)

    def _set_duration(self, v):
        self._duration = v

    @classmethod
    def _validate_float(cls, v, default):
        try:
            return float(v)
        except (ValueError, TypeError):
            return default

#    @on_trait_change('elapsed_time,state')
#    def _update_table(self):
#        #update the analysis table
#        self.update = True

class HeatSchedule(HasTraits):
    steps = List(HeatStep)
    units = Enum('watts', 'temp', 'percent')
    name = Property(depends_on='path')
    path = Str

    load_button = Button('Load')
    save_button = Button('Save')
    save_as_button = Button('Save As')
    add_button = Button('Add Step')

    current_step = Instance(HeatStep)

    selected = List
    selected_index = List
#    elapsed_time = Float

#    @on_trait_change('current_step:elapsed_time')
#    def update_elapsed_time(self, o, n, oo, nn):
##        print o, n, oo, nn
#        self.elapsed_time = nn

#    def reset_steps(self):
#        for s in self.steps:
#            s.state = 'not run'
#            s.elapsed_time = 0
    def _kind_changed(self):
        self.adapter.set_kind(self.units)

    def traits_view(self):
        self.adapter = HeatStepAdapter(kind=self.units)

        editor = TabularEditor(adapter=self.adapter,
                                operations=['delete', 'edit'],
                                multi_select=True,
                                editable=True,
                                auto_update=True,
                                selected='object.selected',
                                selected_row='object.selected_index',
#                                update='object.current_step.update'
                                )
        v = View(
                 VGroup(
                     HGroup(
#                            Spring(width=5,
#                                   springy=False
#                                   ),
                            Item('name',
                                 show_label=False,
                                 style='readonly',
#                                 width=100
                                 ),
                            spring,
                            Item('units', show_label=False),
                            ),
                     Item('steps',
                          show_label=False, editor=editor),
                     HGroup(Item('add_button'),
                            spring,
                            Item('save_as_button',
                                 enabled_when='steps',
                                 ),
                            Item('save_button',
                                 enabled_when='path'
                                ),
                            Item('load_button'),
                            show_labels=False
                        ),
                    show_border=True,
                    label='Heat Schedule'
                    ),
                 )
        return v

#===============================================================================
# persistence
#===============================================================================
    def _dump(self, p):
        with open(p, 'wb') as f:
            pickle.dump(self.steps, f)

    def _load(self, p=None):
        '''
            files ending with .txt loaded as text
            otherwise unpickled
        '''
        if p is None:
            p = self.path
        else:
            self.path = p

        self.steps = []
        if p.endswith('.txt'):
            #load a text file
            for args in parse_file(p, delimiter=','):
                if len(args) == 2:
                    self.steps.append(HeatStep(extract_value=float(args[0]),
                                               duration=float(args[1])
                                               ))
                elif len(args) == 4:
                    for i in range(*map(int, args[:3])):
                        self.steps.append(HeatStep(extract_value=float(i),
                                                   duration=float(args[3])
                                                   ))
        else:
            with open(p, 'rb') as f:
                try:
                    self.steps = pickle.load(f)
                except Exception:
                    pass

#===============================================================================
# button handlers
#===============================================================================

    def _add_button_fired(self):
        ps = self.selected
        if not ps:
            ps = self.steps[-1:]

        for pi in ps:
            self.steps.append(pi.clone_traits())

    def _load_button_fired(self):
        p = self._get_path('open')
        if p is not None:
            self._load(p)

    def _save_button_fired(self):
        self._dump(self.path)

    def _save_as_button_fired(self):
        p = self._get_path('save as')
        if p is not None:
            self.path = p
            self._dump(p)
    def _get_path(self, action):
        d = os.path.join(paths.heating_schedule_dir)
        dlg = FileDialog(action=action,
                         default_directory=d)
        if dlg.open() == OK:
            return dlg.path

    def _get_name(self):
        return os.path.basename(self.path)
#===============================================================================
# debuggin
#===============================================================================
    def _steps_default(self):
        return [
                HeatStep()]
#
#                HeatStep(temp_or_power=0,
#                               duration=5),
#
#                ]
#============= EOF ====================================
