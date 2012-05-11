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



from __future__ import with_statement
#============= enthought library imports =======================
from traits.api import Str, Bool, Property
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.loggable import Loggable

class EnvisageEditable(Loggable):
    file_path = Str
    dirty = Bool
    file_extension = Str
    name = Property(depends_on='file_path')
    _name = Str

    def _get_name(self):
        '''
        '''
#        if not os.path.isfile(self.file_path):
        if not self.file_path:
            if not self._name:
                name = 'New %s' % self.__class__.__name__
            else:
                name = 'New %s' % self._name
        else:
            name = os.path.basename(self.file_path)

        return name

    def _dump_items(self, path, items, use_pickle=True):
        with open(path, 'w') as f:
            self.dirty = False
            self.file_path = path
            if use_pickle:
                pickle.dump(items, f)
            else:
                f.write(items)

    def _pre_save(self, path):
        if path is None:
            path = self.file_path

        path = self.check_file_extension(path)

        oldname = self.name
        return oldname, path

    def check_file_extension(self, path):
        if not path.endswith(self.file_extension):
            path += self.file_extension

        return path
#============= views ===================================
#============= EOF ====================================
