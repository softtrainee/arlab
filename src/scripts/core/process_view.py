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
from traits.api import HasTraits, Str, Enum, List, Instance, Any, \
     on_trait_change, String, Event, Property, Int
from traitsui.api import View, Item, HGroup, spring, ButtonEditor, TabularEditor, ListEditor
#from src.managers.displays.rich_text_display import RichTextDisplay
#from src.scripts.core.scripts_manager import ScriptSelector
from traitsui.tabular_adapter import TabularAdapter
import os

#============= standard library imports ========================

#============= local library imports  ==========================

#============= views ===================================

class ScriptAction(HasTraits):
    text = Str
    script = Any
    state = Enum('notrun', 'stopped', 'finished', 'inprogress')
    line_id = Int
    parent = Any

    @on_trait_change('script:progress_state')
    def state_change(self, new):
        if self.line_id == self.script.active_line:
            self.state = new
            self.parent.update = True


class ProcessAdapter(TabularAdapter):
    columns = [('', 'state'),
             ('Text', 'text')
             ]
    state_image = Property
    state_text = Property

    def get_width(self, obj, trait, column):
        if column == 0:
            return 20
        else:
            return -1

    def _get_state_text(self):
        return ''

    def _get_state_image(self):
        if self.item:
            im = 'gray'
            if self.item.state == 'finished':
                im = 'green'
            elif self.item.state == 'inprogress':
                im = 'yellow'
            elif self.item.state == 'stopped':
                im = 'orange'
            elif self.item.state == 'error':
                im = 'red'

            #get the source path
            root = os.path.split(__file__)[0]
            while not root.endswith('src'):
                root = os.path.split(root)[0]
            root = os.path.split(root)[0]
            root = os.path.join(root, 'resources')

            return os.path.join(root, '{}_ball.png'.format(im))


class Script(HasTraits):
    actions = List(ScriptAction)
    current_action = Any
    name = Str
    update = Event

    def load(self, script):
        self.actions = []
#        print self.name, script
        for i, l in enumerate(script._file_contents_):
            self.actions.append(ScriptAction(script=script,
                                             parent=self,
                                             progress_state='notrun',
                                             text=l,
                                             line_id=i
                                             ))

    def traits_view(self):
        v = View(Item('actions',
                      show_label=False,
                    editor=TabularEditor(adapter=ProcessAdapter(),
                                         update='object.update'),
                    style='custom'
                    ))
        return v


class ProcessView(HasTraits):
    scripts = List(Script)

#    def load_scripts(self, s):
#        for name, si in s:
##            print '{} {}'.format(name, si.file_name)
#            ss = Script(name='{} {}'.format(name, si.file_name))
#            ss.load(si)
#            self.scripts.append(ss)

    def add_script(self, name, script):
        ss = Script(name='{} {}'.format(name, script.file_name))
        ss.load(script)
        self.scripts.append(ss)

    def traits_view(self):
        v = View(Item('scripts',
                      show_label=False,
                      style='custom',
                    editor=ListEditor(use_notebook=True,
                                      page_name='.name')
                    ),
                 resizable=True,
                 width=400,
                 height=200,
                 title='Script Progress'
                 )
        return v
#    name = String
#    execute = Event
#    execute_label = Property(depends_on='alive')
#
#    #experiment = Any
#    #script = Any
#    selected = Any
#    dirty = Bool(True)
#    alive = Bool(False)
#
#    display = Instance(RichTextDisplay)
#    selector = Instance(ScriptSelector)
#    script_manager = Any
#
#    scripts = List
#
#    @on_trait_change('selector:selected')
#    def selector_update(self, obj, name, old, new):
#        self.script_manager.script_klass = new[0]
#        self.script_manager.script_package = new[1]
#        self.script_manager.manager_protocol = new[2]
#
#    def _selector_default(self):
#        return ScriptSelector()
#
#    def _display_default(self):
#        return RichTextDisplay(height=300)
#
#    def _get_execute_label(self):
#
#        return 'STOP' if self.alive else 'EXECUTE'
#
#    def _execute_fired(self):
#        '''
#        '''
#
#        if self.selected:
#            obj = self.selected
#            if self.alive:
#                obj.kill()
#                self.alive = False
#            else:
#                obj.execute()
#
#    def _selected_changed(self, old, new):
#        if new:
#            new._script.on_trait_change(self.update_alive, '_alive')
#            new._script.on_trait_change(self.update_display, '_display_msg')
#
#    def update_display(self, obj, name, old, new):
#        self.display.add_text(new)
#
#    def update_alive(self, obj, name, old, new):
#        '''
#           handle the script death ie not alive
#            
#        '''
#        self.alive = new
#
#    def update_dirty(self, obj, name, old, new):
#        print 'ud', obj, name, old, new
#        self.dirty = new
#
#    def selected_update(self, obj, name, old, new):
#        if name == 'selected':
#            self.selected = new
#            if new is not None:
#                self.name = new.name
##                self.dirty = False
#                new.on_trait_change(self.update_dirty, 'dirty')
#
#    @on_trait_change('selected:name')
#    def name_change(self, obj, name, old, new):
#        '''
#            @type obj: C{str}
#            @param obj:
#
#            @type name: C{str}
#            @param name:
#
#            @type old: C{str}
#            @param old:
#
#            @type new: C{str}
#            @param new:
#        '''
#        #print obj, name, old, new
#        if new is not None:
#            self.name = new
#
#    def traits_view(self):
#        '''
#        '''
#        return View(
#                    HGroup(Item('name'), spring),
#                    HGroup(
#                           Item('execute',
#                                editor=ButtonEditor(label_value='execute_label'),
#                                       #enabled_when = 'experiment or script',
#                                       enabled_when='not dirty',
#                                       show_label=False)
#                            ),
#                            #spring
#                    #Item('selector', show_label = False, style = 'custom'),
#                    Item('display', show_label=False, style='custom')
#                    )

#============= EOF ====================================
