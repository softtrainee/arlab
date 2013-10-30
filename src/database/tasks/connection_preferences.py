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
from pyface.image_resource import ImageResource
from traits.api import Str, Password, Enum, List, Button, Any, Int, \
    on_trait_change, Color
from traitsui.api import View, Item, Group, VGroup, HGroup, ListStrEditor, ButtonEditor, \
    spring, Label
from traitsui.list_str_adapter import ListStrAdapter
from envisage.ui.tasks.preferences_pane import PreferencesPane
from src.database.core.database_adapter import DatabaseAdapter

from src.envisage.tasks.base_preferences_helper import BasePreferencesHelper

#============= standard library imports ========================
#============= local library imports  ==========================
from src.paths import paths
from src.ui.custom_label_editor import CustomLabel


def button_editor(trait, name, editor_kw=None, **kw):
    if editor_kw is None:
        editor_kw = {}

    image = ImageResource(name=name,
                          search_path=paths.icon_search_path)
    return Item(trait,
                style='custom',
                editor=ButtonEditor(image=image, **editor_kw),
                **kw)


class FavoritesAdapter(ListStrAdapter):
    columns = [('', 'name')]
    can_edit = False

    def get_text(self, obj, tr, ind):
        o = getattr(obj, tr)[ind]
        return o.split(',')[0]


class ConnectionPreferences(BasePreferencesHelper):
    preferences_path = 'pychron.database'
    #id = 'pychron.database.preferences_page'

    db_fav_name = Str
    db_name = Str
    db_username = Str
    db_password = Password
    db_host = Str
    db_kind = Enum('---', 'mysql', 'sqlite')
    test_connection = Button

    favorites = List
    add_favorite = Button('+')
    delete_favorite = Button('-')
    selected = Any
    selected_index = Int
    connected_label = Str
    connected_color = Color('green')

    def _test_connection_fired(self):
        db = DatabaseAdapter(username=self.db_username,
                             host=self.db_host,
                             password=self.db_password,
                             name=self.db_name,
                             kind=self.db_kind)

        self.connected_label = ''
        c = db.connect()
        if c:
            self.connected_label = 'Connected'
            self.connected_color = 'green'
        else:
            self.connected_label = 'Not Connected'
            self.connected_color = 'red'


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


class ConnectionPreferencesPane(PreferencesPane):
    model_factory = ConnectionPreferences
    category = 'Database'

    def traits_view(self):
        db_auth_grp = Group(
            Item('db_host', width=125, label='Host'),
            Item('db_username', label='User'),
            Item('db_password', label='Password'),
            enabled_when='db_kind=="mysql"',
            show_border=True,
            label='Authentication'
        )

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
                             button_editor('add_favorite', 'add',
                                           tooltip='Add saved connection'),
                             button_editor('delete_favorite', 'delete',
                                           tooltip='Delete saved connection'),
                             button_editor('test_connection', 'database_connect',
                                           tooltip='Test connection'),
                             spring,
                             Label('Status:'),
                             CustomLabel('connected_label',
                                         label='Status',
                                         weight='bold',
                                         color_name='connected_color'),

                             show_labels=False))

        db_grp = Group(HGroup(Item('db_kind', show_label=False)),
                       Item('db_name', label='Name'),
                       HGroup(fav_grp, db_auth_grp),
                       label='Main DB')

        return View(db_grp)


class MassSpecConnectionPreferences(BasePreferencesHelper):
    preferences_path = 'pychron.database'
    massspec_dbname = Str
    massspec_username = Str
    massspec_password = Password
    massspec_host = Str


class MassSpecConnectionPane(PreferencesPane):
    model_factory = MassSpecConnectionPreferences
    category = 'Database'

    def traits_view(self):
        massspec_grp = Group(
            Group(
                Item('massspec_dbname', label='Database'),
                Item('massspec_host', label='Host'),
                Item('massspec_username', label='Name'),
                Item('massspec_password', label='Password'),
                show_border=True,
                label='Authentication'
            ),
            label='MassSpec DB'
        )

        return View(massspec_grp)

    #============= EOF =============================================
