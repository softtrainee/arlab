#===============================================================================
# Copyright 2013 Jake Ross
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
from pyface.tasks.traits_dock_pane import TraitsDockPane
from traits.api import Instance, Str
from traitsui.api import View, Item, UItem, VGroup

#============= standard library imports ========================
#============= local library imports  ==========================
from src.database.database_connection_spec import DBConnectionSpec


class ConnectionPane(TraitsDockPane):
    name = 'Connection'
    id = 'pychron.sys_mon.connection'

    dbconn_spec = Instance(DBConnectionSpec)
    system_name = Str

    def traits_view(self):
        v = View(VGroup(Item('system_name'),
                        Item('_'),
                        UItem('dbconn_spec', style='custom')))
        return v


#============= EOF =============================================
