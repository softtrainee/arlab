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
from traits.api import HasTraits, Event, Color, Str, Any
from traitsui.api import View, Item
from traitsui.qt4.editor import Editor
#============= standard library imports ========================
from PySide.QtGui import QTextEdit, QPalette, QTextCursor, QTextTableFormat, QTextFrameFormat, \
    QTextTableCellFormat, QBrush, QColor, QFont
from traitsui.basic_editor_factory import BasicEditorFactory
#============= local library imports  ==========================


class _TextTableEditor(Editor):
    _pv = None
    _pc = None
    clear = Event
    refresh = Event
    def init(self, parent):
        '''

        '''
        if self.control is None:
            self.control = QTextEdit()

            if self.factory.bg_color:
                p = QPalette()
                p.setColor(QPalette.Base, self.factory.bg_color)
                self.control.setPalette(p)
            self.control.setReadOnly(True)

        self.object.on_trait_change(self._on_clear, self.factory.clear)

        self.sync_value(self.factory.refresh, 'refresh', mode='from')
#        parent.addStretch(1)
#        parent.addWidget(self.control)
    def _refresh_fired(self):
        self.update_editor()

    def _on_clear(self):
        pass
#        if self.control:
#            self.control.clear()

    def update_editor(self, *args, **kw):
        '''
        '''

        self.control.clear()
        adapter = self.factory.adapter
        tables = adapter.make_tables(self.value)
        for ti in tables:
            self._add_table(ti)

    def _add_table(self, tab):
        cursor = QTextCursor(self.control.textCursor())

        tab_fmt = QTextTableFormat()
        tab_fmt.setCellSpacing(0)
        tab_fmt.setCellPadding(3)

        border = tab.border
        if border:
            tab_fmt.setBorderStyle(QTextFrameFormat.BorderStyle_Solid)
        else:
            tab_fmt.setBorderStyle(QTextFrameFormat.BorderStyle_None)

        cursor.insertTable(tab.rows(), tab.cols(), tab_fmt)
        table = cursor.currentTable()

        bc = QColor(self.factory.bg_color) if self.factory.bg_color else None
        ec, oc, hc = bc, bc, bc
        if self.factory.even_color:
            ec = QColor(self.factory.even_color)
        if self.factory.odd_color:
            oc = QColor(self.factory.odd_color)
        if self.factory.header_color:
            hc = QColor(self.factory.header_color)

        cell_fmt = QTextTableCellFormat()
        cell_fmt.setFontPointSize(10)
        for ri, row in enumerate(tab.items):
            c = bc
            if row.color:
                c = QColor(row.color)
            elif ri == 0:
                c = hc
            else:
                if (ri - 1) % 2 == 0:
                    c = ec
                else:
                    c = oc
            if c:
                cell_fmt.setBackground(c)

            for ci, cell in enumerate(row.cells):
                if cell.bg_color:
                    cell_fmt.setBackground(QColor(cell.bg_color))
                if cell.bold:
                    cell_fmt.setFontWeight(QFont.Bold)
                else:
                    cell_fmt.setFontWeight(QFont.Normal)

                tcell = table.cellAt(ri, ci)
                tcell.setFormat(cell_fmt)
                tcell.firstCursorPosition().insertText(cell.text)


class TextTableEditor(BasicEditorFactory):
    klass = _TextTableEditor
    bg_color = Color
    odd_color = Str
    even_color = Str
    header_color = Str
    clear = Str
    adapter = Any
    refresh = Str
#============= EOF =============================================
