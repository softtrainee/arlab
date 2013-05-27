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
from PySide.QtGui import QKeySequence, QDrag, QAbstractItemView, QFontMetrics, QFont
from PySide import QtCore
from traits.api import Bool, on_trait_change, Any, Str, Event, List, Callable
from traitsui.editors.tabular_editor import TabularEditor
from traitsui.qt4.tabular_editor import TabularEditor as qtTabularEditor, \
    _TableView
from traitsui.mimedata import PyMimeData
#============= standard library imports ========================
#============= local library imports  ==========================

class _myTableView(_TableView):
    '''
        for drag and drop reference see
        https://github.com/enthought/traitsui/blob/master/traitsui/qt4/tree_editor.py
        
    '''
    _copy_cache = None
    copy_func = None
    _dragging = None

    def __init__(self, *args, **kw):
        super(_myTableView, self).__init__(*args, **kw)
        self.setDragDropMode(QAbstractItemView.DragDrop)

        editor = self._editor
        # reimplement row height
        vheader = self.verticalHeader()
#        size = vheader.minimumSectionSize()
#        print size
        size = 10
        font = editor.adapter.get_font(editor.object, editor.name, 0)
        if font is not None:
            size = max(size, QFontMetrics(QFont(font)).height())
        vheader.setDefaultSectionSize(size)

    def keyPressEvent(self, event):

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
                    idx = si[0].row()
                else:
                    idx = len(self._editor.value) + 1

                for ci in reversed(self._copy_cache):
                    self._editor.model.insertRow(idx, obj=copy_func(ci))
        else:
            super(_myTableView, self).keyPressEvent(event)

    def startDrag(self, actions):
        if self._editor.factory.drag_external:
            idxs = self.selectedIndexes()
            rows = sorted(list(set([idx.row() for idx in idxs])))
            drag_object = [
                           (ri, self._editor.value[ri])
                            for ri in rows]

            md = PyMimeData.coerce(drag_object)

            self._dragging = self.currentIndex()
            drag = QDrag(self)
            drag.setMimeData(md)
    #        drag.setPixmap(pm)
    #        drag.setHotSpot(hspos)
            drag.exec_(actions)
        else:
            super(_myTableView, self).startDrag(actions)


    def dragEnterEvent(self, e):
        if self.is_external():
            # Assume the drag is invalid.
            e.ignore()

            # Check what is being dragged.
            md = PyMimeData.coerce(e.mimeData())
            if md is None:
                return

            # We might be able to handle it (but it depends on what the final
            # target is).
            e.acceptProposedAction()
        else:
            super(_myTableView, self).dragEnterEvent(e)

    def dragMoveEvent(self, e):
        if self.is_external():
            e.acceptProposedAction()
        else:
            super(_myTableView, self).dragMoveEvent(e)

    def dropEvent(self, e):
        if self.is_external():
            data = PyMimeData.coerce(e.mimeData()).instance()
            copy_func = lambda x: x

            row = self.rowAt(e.pos().y())
            n = len(self._editor.value)
            if row == -1:
                row = n

            model = self._editor.model
            if self._dragging:
                rows = [ri for ri, _ in data]
                model.moveRows(rows, row)
            else:
#                self._editor._no_update = True
#                parent = QtCore.QModelIndex()
#                model.beginInsertRows(parent, row, row)
#                editor = self._editor
                self._editor.object._no_update = True
                for i, (_, di) in enumerate(reversed(data[1:])):
#                    print 'insert'
#                    obj = copy_func1(di)
#                    editor.callx(editor.adapter.insert, editor.object, editor.name, row + i, obj)
                    model.insertRow(row=row, obj=copy_func(di))

                self._editor.object._no_update = False
                model.insertRow(row=row, obj=copy_func(data[0][1]))


#                model.endInsertRows()
#                self._editor._no_update = False

            e.accept()
            self._dragging = None

        else:
            super(_myTableView, self).dropEvent(e)


    def is_external(self):
#        print 'is_external', self._editor.factory.drag_external and not self._dragging
        return self._editor.factory.drag_external  # and not self._dragging

class _TabularEditor(qtTabularEditor):

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
        for i in range(3):
            self.control.scrollTo(self.model.index(row, 0), scroll_hint)


class myTabularEditor(TabularEditor):
    scroll_to_bottom = Bool(True)
    scroll_to_row_hint = 'visible'
#    scroll_to_row_hint = 'bottom'
#    drag_move = Bool(False)
    rearranged = Str
    pasted = Str
    copy_cache = Str
    copy_function = Str
    drag_external = Bool(False)
    def _get_klass(self):
        return _TabularEditor
#============= EOF =============================================
