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
from traits.api import HasTraits, Str, Password, Enum, List, Button, Any, Int, \
    on_trait_change
from traitsui.api import View, Item, Group, VGroup, HGroup, ListStrEditor
from src.envisage.tasks.base_preferences_helper import BasePreferencesHelper
from traitsui.list_str_adapter import ListStrAdapter
from envisage.ui.tasks.preferences_pane import PreferencesPane
#============= standard library imports ========================
#============= local library imports  ==========================
class FavoritesAdapter(ListStrAdapter):
    columns = [('', 'name')]
    can_edit = False
    def get_text(self, obj, tr, ind):
        o = getattr(obj, tr)[ind]
        return o.split(',')[0]

class ExperimentPreferences(BasePreferencesHelper):
    name = 'Experiment'
    preferences_path = 'pychron.experiment'
    id = 'pychron.experiment.preferences_page'
#    username = Str

    db_fav_name = Str
    db_name = Str
    db_username = Str
    db_password = Password
    db_host = Str
    db_kind = Enum('---', 'mysql', 'sqlite')

#    repo_kind = Enum('---', 'local', 'FTP')
#
#    ftp_username = Str
#    ftp_password = Password
#    ftp_host = Str
#    repo_root = Str

    massspec_dbname = Str
    massspec_username = Str
    massspec_password = Password
    massspec_host = Str

    favorites = List
    add_favorite = Button('+')
    delete_favorite = Button('-')
    selected = Any
#    selected_live = Any
    selected_index = Int

    @on_trait_change('db+')
    def db_attribute_changed(self, obj, name, old, new):
        if name == 'db_fav_name':
            return

        if self.favorites:
            for i, fastr in enumerate(self.favorites):
                vs = fastr.split(',')
                if vs[0] == self.db_fav_name:
                    aind = ['', 'db_kind', 'db_username', 'db_host', 'db_name', 'db_password'].index(name)
                    fa = fastr.split(',')
                    fa[aind] = new
                    fastr = ','.join(fa)
                    self.favorites[i] = fastr
                    self.selected = fastr
                    break

    def _selected_changed(self):
        sel = self.selected
        if isinstance(sel, (str, unicode)):
            vs = sel.split(',')
            for v, attr in zip(vs, ['fav_name', 'kind', 'username',
                                    'host', 'name', 'password']):
                setattr(self, 'db_{}'.format(attr), str(v))

    def _delete_favorite_fired(self):
        if self.selected:
            if self.favorites:
                if self.selected in self.favorites:
                    self.favorites.remove(self.selected)

            if self.favorites:
                self.selected = self.favorites[-1]
            else:
                vs = ['', '---', '', '', '', '']
                for v, attr in zip(vs, ['fav_name', 'kind', 'username',
                                    'host', 'name', 'password']):
                    setattr(self, 'db_{}'.format(attr), str(v))


    def _add_favorite_fired(self):
        if self.db_fav_name:
            fv = ','.join([self.db_fav_name,
                           self.db_kind,
                           self.db_username, self.db_host,
                           self.db_name,
                           self.db_password
                           ])

            pf = next((f for f in self.favorites if f.split(',')[0] == self.db_fav_name), None)
            if pf:
                ind = self.favorites.index(pf)
                self.favorites.remove(pf)
                self.favorites.insert(ind, fv)

            else:
                self.favorites.append(fv)

            self.selected = fv

class ExperimentPreferencesPane(PreferencesPane):
    model_factory = ExperimentPreferences

    def traits_view(self):

        db_auth_grp = Group(
                            Item('db_host', width=125, label='Host'),
                            Item('db_username', label='User'),
                            Item('db_password', label='Password'),
                            enabled_when='db_kind=="mysql"',
                            show_border=True,
                            label='Authentication'
                            )

#        ftp_auth_grp = Group(Item('ftp_host', label='Host'),
#                             Item('ftp_username', label='Name'),
#                             Item('ftp_password', label='Password'),
#                             Item('repo_root', label='Data directory'),
#                             enabled_when='repo_kind=="FTP"',
#                             show_border=True,
#                             label='Authentication'
#                             )

        fav_grp = VGroup(Item('db_fav_name',
#                              editor=EnumEditor(name='favorites'),
                              show_label=False),
                         Item('favorites',
                              show_label=False,
                              width=100,
                              editor=ListStrEditor(
                                                   editable=False,
                                                   adapter=FavoritesAdapter(),
                                                   selected='object.selected',
                                                   )),
                         HGroup(
                                Item('add_favorite'),
                                Item('delete_favorite'),
                                show_labels=False

                                )
                         )

        db_grp = Group(HGroup(Item('db_kind', show_label=False)),
                       Item('db_name', label='Name'),
                       HGroup(fav_grp, db_auth_grp),
                       show_border=True, label='Database')

#        repo_grp = Group(
#                         Item('repo_kind', show_label=False),
#                         ftp_auth_grp,
#                         show_border=True, label='Repo'
#                         )
# #
        massspec_grp = Group(
                             Group(
                                 Item('massspec_dbname', label='Database'),
                                 Item('massspec_host', label='Host'),
                                 Item('massspec_username', label='Name'),
                                 Item('massspec_password', label='Password'),
                                 show_border=True,
                                 label='MassSpec Authentication'
                                 ),
                             label='MassSpec'
                             )
        return View(
#                        user_grp,
                        db_grp,
#                        repo_grp,
                        massspec_grp,
                    )

#============= EOF =============================================
