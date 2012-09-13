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
from traits.api import Str, Password, Enum
from traitsui.api import View, Item, TableEditor, Group, VGroup, HGroup, spring
from apptools.preferences.ui.preferences_page import PreferencesPage
#============= standard library imports ========================
#============= local library imports  ==========================
class ExperimentPreferencesPage(PreferencesPage):
    name = 'Experiment'
    preferences_path = 'pychron.experiment'

    username = Str

    db_name = Str
    db_username = Str
    db_password = Password
    db_host = Str
    db_kind = Enum('mysql', 'sqlite')

    repo_kind = Enum('local', 'FTP')

    ftp_username = Str
    ftp_password = Password
    ftp_host = Str
    repo_root = Str


    def traits_view(self):
        user_grp = Group(
                         Item('username'),
                         label='User'
                         )

        db_auth_grp = Group(Item('db_host', label='Host'),
                            Item('db_username', label='Name'),
                            Item('db_password', label='Password'),
                            enabled_when='db_kind=="mysql"',
                            show_border=True,
                            label='Authentication'
                            )

        ftp_auth_grp = Group(Item('ftp_host', label='Host'),
                             Item('ftp_username', label='Name'),
                             Item('ftp_password', label='Password'),
                             Item('repo_root', label='Data directory'),
                             enabled_when='repo_kind=="FTP"',
                             show_border=True,
                             label='Authentication'
                             )

        db_grp = Group(HGroup(Item('db_kind', show_label=False)),
                       Item('db_name', label='Name'),
                       db_auth_grp,
                       show_border=True, label='Database')

        repo_grp = Group(
                         Item('repo_kind', show_label=False),
                         ftp_auth_grp,
                         show_border=True, label='Repo'
                         )
        return View(
                        user_grp,
                        db_grp,
                        repo_grp
                    )
#============= EOF =============================================
