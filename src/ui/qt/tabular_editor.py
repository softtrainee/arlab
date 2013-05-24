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
from traits.api import Bool, on_trait_change, Any, Str, Event, List, Callable
from traitsui.editors.tabular_editor import TabularEditor
from traitsui.qt4.tabular_editor import TabularEditor as qtTabularEditor, \
    _TableView
# from traitsui.wx.tabular_editor import TabularEditor as wxTabularEditor
#============= standard library imports ========================
#============= local library imports  ==========================

class _myTableView(_TableView):
    _copy_cache = None
    copy_func = None
    def keyPressEvent(self, event):
#        print event.key(), event.text()
#        print event.nativeModifiers()


        if event.matches(QKeySequence.Copy):
            self._copy_cache = [self._editor.value[ci.row()] for ci in
                                    self.selectionModel().selectedRows()]

        elif event.matches(QKeySequence.Paste):
            if self._copy_cache:
                si = self.selectedIndexes()
                copy_func = self.copy_func
                if copy_func is None:
                    copy_func = lambda x: x.clone_traits()
                if len(si):
                    idx = si.row()
                else:
                    idx = -1

                for ci in reversed(self._copy_cache):
                    self._editor.model.insertRow(idx, obj=copy_func(ci))
                self._editor.pasted = True
        else:
            super(_myTableView, self).keyPressEvent(event)

class _TabularEditor(qtTabularEditor):
#    drop_target = Any
#    rearranged = Event
#    pasted = Event
#
#    copy_cache = List

    widget_factory = _myTableView

    def init(self, parent):
        super(_TabularEditor, self).init(parent)


#        self.sync_value(self.factory.rearranged, 'rearranged', 'to')
#        self.sync_value(self.factory.pasted, 'pasted', 'to')
#        self.sync_value(self.factory.copy_cache, 'copy_cache', 'to')

        if hasattr(self.object, self.factory.copy_function):
            self.control.copy_func = getattr(self.object, self.factory.copy_function)

    def _copy_function_changed(self):
        if self.control:
            self.control.copy_func = self.copy_function

    def refresh_editor(self):
        if self.control:
            super(_TabularEditor, self).refresh_editor()

    def _scroll_to_row_changed(self, row):
        """ Scroll to the given row.
        """
        scroll_hint = self.scroll_to_row_hint_map.get(self.factory.scroll_to_row_hint, self.control.PositionAtCenter)

        '''
            for some reason only one call to scrollTo was not working consistently
        '''
        self.control.scrollTo(self.model.index(row, 0), scroll_hint)
        self.control.scrollTo(self.model.index(row, 0), scroll_hint)

#            self.control.scrollTo(self.model.index(row, 0), scroll_hint)
#        print self.control
#        print len(self.value)
#    def update_editor(self):

#        m = len(self.value) - 1
#        print self.factory.scroll_to_bottom, m
#        if self.factory.scroll_to_bottom:
#            self.scroll_to_row = m
#            if not self.selected and not self.multi_selected:
#                print m, 'a'
# #                self.callx(self.trait_set, scroll_to_row=m - 1)
#                self.scroll_to_row = m - 1
# #                 control.EnsureVisible(control.GetItemCount() - 1)
#            else:
#                if self.selected_row != -1:
#                    print min(m, self.selected_row + 1), 'b'
#                    self.scroll_to_row = min(m, self.selected_row + 1)
#
# #                    control.EnsureVisible(self.selected_row + 1)
#                elif self.multi_selected_rows:
#                    print m, 'c'
#                    self.scroll_to_row = min(m, self.multi_selected_rows[-1] + 1)

 #                    control.EnsureVisible(self.multi_selected_rows[-1] + 1)

 #        else:
 #            if not self.selected and not self.multi_selected:
 #                control.EnsureVisible(0)
#        super(_TabularEditor, self).update_editor()

#    def wx_dropped_on (self, x, y, data, drag_result):
#        super(_TabularEditor, self).wx_dropped_on (x, y, data, drag_result)
#        self.rearranged = True

#    def _move_up_current (self):
#        super(_TabularEditor, self)._move_up_current()
#        self.rearranged = True
#
#    def _move_down_current (self):
#        super(_TabularEditor, self)._move_down_current()
#        self.rearranged = True
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
    scroll_to_row_hint = 'visible'
#    scroll_to_row_hint = 'bottom'
#    drag_move = Bool(False)
    rearranged = Str
    pasted = Str
    copy_cache = Str
    copy_function = Str
    def _get_klass(self):
        return _TabularEditor
#============= EOF =============================================
