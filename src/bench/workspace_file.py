#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.api import HasTraits, Bool, Str
from traitsui.api import View, Item
#============= standard library imports ========================
import os
#============= local library imports  ==========================


class WorkspaceFile(HasTraits):
    dirty = Bool(False)
    text = Str
    path = Str
    _otext = None

    def __init__(self, path, *args, **kw):
        self.reload(path=path)

        super(WorkspaceFile, self).__init__(*args, **kw)

    def _text_changed(self):
        if self.text != self._otext:
            self.dirty = True
        else:
            self.dirty = False

    def reload(self, path=None):
        if path is None:
            path = self.path

        if os.path.isfile(path):
            self.path = path
            with open(path, 'r') as f:
                self.text = f.read()

            self._otext = self.text
            self.dirty = False

    def dump(self):
        with open(self.path, 'w') as f:
            f.write(self.text)

    def traits_view(self):
        v = View(Item('text', show_label=False, style='custom'))
        return v
#============= EOF =============================================
