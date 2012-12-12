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



'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#=============enthought library imports=======================
from traits.api import Instance, Str
from traitsui.api import View, Item, Group, HGroup, spring, \
    EnumEditor
#=============standard library imports ========================
import os
#=============local library imports  ==========================
from manager_script import ManagerScript
from src.managers.displays.rich_text_display import RichTextDisplay
#from src.managers.displays.rich_text_display import StyledTextDisplay
from src.helpers.color_generators import colors8i as colors
from src.helpers.filetools import parse_file

class FileScript(ManagerScript):
    '''
        G{classtree}
    '''
    _file_contents_ = None
    source_dir = None
    progress_display = Instance(RichTextDisplay)
    file_name = Str
    available_scripts = None
    def __init__(self, *args, **kw):
        '''
            @type *args: C{str}
            @param *args:

            @type **kw: C{str}
            @param **kw:
        '''
        super(FileScript, self).__init__(*args, **kw)
        self.available_scripts = []

    def open(self):
        '''
        '''
        if self.source_dir is not None:
            if os.path.isdir(self.source_dir):
                files = os.listdir(self.source_dir)

                files = [f for f in files
                            if not os.path.basename(f).startswith('.') and
                                os.path.isfile(os.path.join(self.source_dir, f)) ]

                self.available_scripts = files
                self.file_name = files[0]
                self.edit_traits(view='progress_view')
            else:
                self.warning('Invalid directory %s' % self.source_dir)
        else:
            self.warning('Source directory is None')

    def load_file_contents(self):
        '''
        '''
        p = os.path.join(self.source_dir, self.file_name)
        self.file_path = p
        self._file_contents_ = parse_file(p)

    def _start_fired(self):
        '''
        '''
        return self.bootstrap()

    def bootstrap(self, condition=None):
        '''
            @type condition: C{str}
            @param condition:
        '''
        self.condition = condition
        self.load_file_contents()
        if not self.load_file():

            if self.load():
                self.start()

                #we are started so update running flag
                return True


    def add_display_text(self, msg, color=None, log=False):
        '''
            @type msg: C{str}
            @param msg:

            @type color: C{str}
            @param color:

            @type log: C{str}
            @param log:
        '''
        if not color:
            color = colors['black']

        elif isinstance(color, str):
            color = colors[color]

        self.progress_display.add_text(msg=msg, color=color)
        if log:
            self.info('%s' % msg)
    def load(self):
        '''
        '''
        if self.set_data_frame():
            self.set_graph()
            return True

    def load_file(self):
        '''
        '''
        raise NotImplementedError

    def set_graph(self):
        '''
        '''
        pass



    def _info_group_factory(self):
        '''
        '''
        g = Group(Item('progress_display', show_label=False, style='custom'),)
        return g

    def progress_view(self):
        '''
        '''

        return View(Item('default_save'),
                    self._button_group_factory(),
                    HGroup(Item('file_name', editor=EnumEditor(values=self.available_scripts), show_label=False), spring),
                    self._info_group_factory(),
                    x=10,
                    y=20,
                    title='Script Progress',
                    resizable=True,
                    )

#=========== defaults ===========
    def _progress_display_default(self):
        '''
        '''
        return RichTextDisplay(width=100)
#=========== EOF ================
