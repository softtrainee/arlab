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
from traits.api import Any, Button, Dict, List, on_trait_change
from traitsui.api import View, Item, TableEditor
#============= standard library imports ========================
from threading import Event, Lock
#============= local library imports  ==========================
from src.helpers.logger_setup import logging_setup
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn
from src.viewable import Viewable


class PyScriptRunner(Viewable):
    resources = Dict
    _resource_lock = Any
    scripts = List

#    @on_trait_change('scripts[]')
#    def _scripts_changed(self, obj, name, old, new):
#        if not len(self.scripts):
#            self.close_ui()

    def __resource_lock_default(self):
        return Lock()

    def get_resource(self, resource):
        with self._resource_lock:
            if not resource in self.resources:
                self.resources[resource] = Event()

            r = self.resources[resource]
            return r

    def traits_view(self):

        cols = [ObjectColumn(name='logger_name', label='Name',
                              editable=False, width=150),
                CheckboxColumn(name='cancel_flag', label='Cancel',
                               width=50),
              ]
        v = View(Item('scripts', editor=TableEditor(columns=cols,
                                                    auto_size=False),
                      show_label=False
                      ),
                 width=500,
                 height=500,
                 resizable=True,
                 handler=self.handler_klass(),
                 title='ScriptRunner'
                 )
        return v

if __name__ == '__main__':
    logging_setup('py_runner')
    p = PyScriptRunner()

    p.configure_traits()
#============= EOF ====================================
