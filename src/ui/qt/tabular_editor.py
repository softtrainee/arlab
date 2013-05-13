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
from PySide.QtGui import QKeySequence
from traits.api import Bool, on_trait_change, Any, Str, Event, List
from traitsui.editors.tabular_editor import TabularEditor
from traitsui.qt4.tabular_editor import TabularEditor as qtTabularEditor, \
    _TableView
# from traitsui.wx.tabular_editor import TabularEditor as wxTabularEditor
#============= standard library imports ========================
#============= local library imports  ==========================

class _myTableView(_TableView):
    _copy_cache = None
    def keyPressEvent(self, event):
#        print event.key(), event.text()
#        print event.nativeModifiers()

        if event.matches(QKeySequence.Copy):
            self._copy_cache = self.selectionModel().selectedRows()
        elif event.matches(QKeySequence.Paste):
            if self._copy_cache:
                for ci in self._copy_cache:

                    obj = self._editor.value[ci.row()]
#                    ri=self.selectionModel()
                    self._editor.model.insertRow(0, obj=obj)
                self._editor.pasted = True
        else:
            super(_myTableView,self).keyPressEvent(event)

class _TabularEditor(qtTabularEditor):
#    drop_target = Any
    rearranged = Event
    pasted = Event

    copy_cache = List

    widget_factory = _myTableView

    def init(self, parent):
        super(_TabularEditor, self).init(parent)

#        control = self.control
#        control.connect()
#        control.keyPressEvent.connect(self._on_key)
#        control.connect(control, SIGNAL("keyPressEvent(event)"), self._on_key)

#        control.itemClicked.connect(self._on_key)
#        print control
#        control.Bind(wx.EVT_KEY_DOWN, self._on_key)

        # binding to the EVT_MOTION prevents the EVT_LIST_BEGIN_DRAG from firing
        # remove binding added by wxTabularEditor
#        control.Bind(wx.EVT_MOTION, None)

        self.sync_value(self.factory.rearranged, 'rearranged', 'to')
        self.sync_value(self.factory.pasted, 'pasted', 'to')
        self.sync_value(self.factory.copy_cache, 'copy_cache', 'to')

#    def update_editor(self):
#        super(_TabularEditor, self).update_editor()
#
#        control = self.control
#        if self.factory.scroll_to_bottom:
#            if not self.selected and not self.multi_selected:
#                control.
# #                control.EnsureVisible(control.GetItemCount() - 1)
#            else:
#
#                if self.selected_row != -1:
#                    control.EnsureVisible(self.selected_row + 1)
#                elif self.multi_selected_rows:
#                    control.EnsureVisible(self.multi_selected_rows[-1] + 1)
#
#        else:
#            if not self.selected and not self.multi_selected:
#                control.EnsureVisible(0)

#    def wx_dropped_on (self, x, y, data, drag_result):
#        super(_TabularEditor, self).wx_dropped_on (x, y, data, drag_result)
#        self.rearranged = True

    def _move_up_current (self):
        super(_TabularEditor, self)._move_up_current()
        self.rearranged = True

    def _move_down_current (self):
        super(_TabularEditor, self)._move_down_current()
        self.rearranged = True
    #    def _on_motion(self, event):
#        print event
#        event.Skip()

#    def _begin_rdrag(self, event):
#        print 'r', event

#    def _begin_drag(self, event):
#        print 'ffff', event
#        adapter = self.adapter
#        object, name = self.object, self.name
#        selected = self._get_selected()
#        drag_items = []
#        for row in selected:
#            drag = adapter.get_drag(object, name, row)
#            if drag is None:
#                return
#
#            drag_items.append(drag)
#
#        PythonDropSource(self.drop_target, drag_items)

class myTabularEditor(TabularEditor):
    scroll_to_bottom = Bool(True)
    drag_move = Bool(False)
    rearranged = Str
    pasted = Str
    copy_cache = Str
    def _get_klass(self):
        return _TabularEditor
#============= EOF =============================================
