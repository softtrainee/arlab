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
from traits.api import List, Button, Any, Int, Str
from traitsui.api import UItem, ButtonEditor
from apptools.preferences.api import PreferencesHelper
#============= standard library imports ========================
#============= local library imports  ==========================
from traitsui.list_str_adapter import ListStrAdapter
from src.paths import paths


def button_editor(trait, name, editor_kw=None, **kw):
    if editor_kw is None:
        editor_kw = {}

    image = ImageResource(name=name,
                          search_path=paths.icon_search_path)
    return UItem(trait,
                 style='custom',
                 editor=ButtonEditor(image=image, **editor_kw),
                 **kw)


class FavoritesAdapter(ListStrAdapter):
    columns = [('', 'name')]
    can_edit = False

    def get_text(self, obj, tr, ind):
        o = getattr(obj, tr)[ind]
        return o.split(',')[0]


class BasePreferencesHelper(PreferencesHelper):
    pass


class FavoritesPreferencesHelper(BasePreferencesHelper):
    favorites = List
    fav_name = Str

    add_favorite = Button('+')
    delete_favorite = Button('-')
    selected = Any
    selected_index = Int

    def _get_attrs(self):
        raise NotImplementedError

    def _get_values(self):
        raise NotImplementedError

    def _selected_changed(self):
        sel = self.selected
        if isinstance(sel, (str, unicode)):
            vs = sel.split(',')
            for v, attr in zip(vs, self._get_attrs()):
                setattr(self, attr, str(v))

    def _delete_favorite_fired(self):
        if self.selected:
            if self.favorites:
                if self.selected in self.favorites:
                    self.favorites.remove(self.selected)

            if self.favorites:
                self.selected = self.favorites[-1]
            else:
                vs = ['', '---', '', '', '', '']
                for v, attr in zip(vs, self._get_attrs()):
                    setattr(self, attr, str(v))

    def _add_favorite_fired(self):
        if self.fav_name:
            fv = ','.join(self._get_values())
            pf = next((f for f in self.favorites
                       if f.split(',')[0] == self.fav_name), None)
            if pf:
                ind = self.favorites.index(pf)
                self.favorites.remove(pf)
                self.favorites.insert(ind, fv)

            else:
                self.favorites.append(fv)

            self.selected = fv

#============= EOF =============================================
