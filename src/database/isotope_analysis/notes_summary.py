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
from traits.api import HasTraits, List, Any, Str, Button, Property, Int, Instance, \
     on_trait_change, Event
from traitsui.api import View, Item, HGroup, TabularEditor, VGroup, spring
from traitsui.tabular_adapter import TabularAdapter

#============= standard library imports ========================
#============= local library imports  ==========================
# class Note(HasTraits):
#    pass

class NotesTabularAdapter(TabularAdapter):
    columns = [('User', 'user'), ('Date', 'create_date')]

    user_text = Property
    user_width = Int(50)
    create_date_width = Int(120)

    def get_font(self, obj, trait, row):
        import wx
        s = 9
        f = wx.FONTFAMILY_DEFAULT
        st = wx.FONTSTYLE_NORMAL
#        w = wx.FONTWEIGHT_BOLD
        w = wx.FONTWEIGHT_NORMAL
        name = 'Bitstream Vera Sans Mono'
        return wx.Font(s, f, st, w, False, name)

    def _get_user_text(self):
        u = self.item.user
        return u if u is not None else '---'

class NoteHistoryView(HasTraits):
    notes = List
    def traits_view(self):
        v = View(Item('notes', show_label=False,
                          editor=TabularEditor(
                                     adapter=NotesTabularAdapter(),
                                     editable=False,
                                     operations=[],
                                     auto_update=True,
                                     horizontal_lines=True,
                                     selected='object.summary.selected_note'
                                     )),)
        return v

class NoteView(HasTraits):
    add_note = Button('Add Note')
    record = Any
    note_text = Str
    new_note = Str
    note_added = Event
    def _add_note_fired(self):
        if self.new_note and self.new_note.strip():
            note = self.record.add_note(self.new_note)
            self.note_added = note

    def traits_view(self):
        v = View(VGroup(
                      Item('note_text', show_label=False,
                            style='custom',
                            height=0.7
                            ),
                      Item('new_note', style='custom',
                            height=0.3,
                            show_label=False),
                      HGroup(Item('add_note', show_label=False), spring)
                    )
               )
        return v

class Note(HasTraits):
    dbnote = Any
    def __getattr__(self, attr):
        return getattr(self.dbnote, attr)

class NotesSummary(HasTraits):
    selected_note = Any
    note_history_view = Instance(NoteHistoryView)
    note_view = Instance(NoteView)
    record = Any

    @on_trait_change('note_view:note_added')
    def _note_added(self, new):
        self.note_history_view.notes.append(Note(dbnote=new))
        self.selected_note = self.note_history_view.notes[-1]

    def _selected_note_changed(self):
        if self.selected_note:
            self.note_view.note_text = self.selected_note.note

    def _note_view_default(self):
        return NoteView(record=self.record)

    def _note_history_view_default(self):
        notes = [Note(dbnote=ni) for ni in self.record.dbrecord.notes]
        if notes:
            self.note_view.note_text = notes[-1].note

        return NoteHistoryView(notes=notes, summary=self)

    def traits_view(self):
        v = View(HGroup(
                        Item('note_history_view', style='custom',
                             show_label=False,
                             width=0.19),
                        Item('note_view', style='custom', show_label=False,
                             width=self.record.item_width * 0.73
                             )
                        )
                 )
        return v
#============= EOF =============================================
