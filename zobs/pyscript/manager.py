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
from traits.api import HasTraits
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
#============= local library imports  ==========================

from src.managers.manager import Manager
from src.paths import paths


class PyScriptManager(Manager):
    def _extract_kind(self, path):
        with open(path, 'r') as fp:
            for line in fp:
                if line.startswith('#!'):
                    return line.strip()[2:].lower()


    def open_script(self, path=None):
        '''
            open and load a new pyscript editor
            
            determine editor type by a shebang
        '''

        if path is None:
            path = self.open_file_dialog(default_directory=paths.scripts_dir)


        if path is not None:
#            kind = 'measurement'
            # get script kind
            kind = self._extract_kind(path)
            if kind == 'measurement':
                from src.pyscripts.measurement_editor import MeasurementPyScriptEditor
                klass = MeasurementPyScriptEditor
            else:
                from src.pyscripts.editor import PyScriptEditor
                klass = PyScriptEditor

            editor = klass()
            if editor.open_script(path):
                return editor
#============= EOF =============================================
