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
from traits.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = 'qt4'

#============= enthought library imports =======================
from traits.api import HasTraits, Str, List, Instance, Any, Button, Date
from traitsui.api import View, Item, UItem, ButtonEditor, TabularEditor, \
    HGroup
from traitsui.tabular_adapter import TabularAdapter
from src.paths import paths
from pyface.image_resource import ImageResource

#============= standard library imports ========================
#============= local library imports  ==========================

class Tag(HasTraits):
    name = Str
    user = Str
    date = Date


class TagTable(HasTraits):
    tags = List
    db = Any
    def load(self):
        db = self.db
        with db.session_ctx():
            dbtags = db.get_tags()
            self.tags = [Tag(name=di.name,
                           user=di.user,
                           date=di.create_date
                           )
                           for di in dbtags]

    def add_tag(self, tag):
        name, user = tag.name, tag.user
        db = self.db
        with db.session_ctx():
            db.add_tag(name=name, user=user)

        self.load()

    def delete_tag(self, tag):
        if isinstance(tag, str):
            tag = next((ta for ta in self.tags if ta.name == tag), None)
            print tag
        if tag:
            self.tags.remove(tag)


class TagAdapter(TabularAdapter):
    columns = [('Name', 'name'), ('User', 'user'),
               ('Date', 'date')
               ]

class TagTableView(HasTraits):
    table = Instance(TagTable, ())
    add_tag_button = Button
    delete_tag_button = Button
    selected = Any

    def _add_tag_button_fired(self):
        n = Tag()
        tag_view = View(Item('name'), Item('user'),
                        buttons=['OK', 'Cancel']
                        )
        info = n.edit_traits(kind='livemodal', view=tag_view)
        if info.result:
            self.table.add_tag(n)

    def _delete_tag_button_fired(self):
        s = self.selected
        if s:
            if not isinstance(s, list):
                s = (s,)
            for si in s:
                self.table.delete_tag(si)

    def traits_view(self):

        v = View(UItem('object.table.tags',
                        editor=TabularEditor(adapter=TagAdapter(),
                                            editable=False,
                                            operations=[],
                                            selected='selected',
#                                             multi_select=True
                                            ),
                       ),
                 HGroup(
                     UItem('add_tag_button',
                           style='custom',
                           editor=ButtonEditor(image=ImageResource(name='add.png',
                                                                   search_path=paths.icon_search_path))
                           ),
#                      UItem('delete_tag_button',
#                            style='custom',
#                            editor=ButtonEditor(image=ImageResource(name='delete.png',
#                                                                    search_path=ps))
#                            )
                        ),

                 resizable=True,
                 width=500,
                 height=400,
                 buttons=['OK', 'Cancel'],
                 kind='livemodal'
#                  buttons=['Apply']
                 )
        return v

if __name__ == '__main__':
    t = TagTableView()
    t.table.tags = [Tag(name='foo') for i in range(10)]
    t.configure_traits()
#============= EOF =============================================
