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
from traitsui.qt4.basic_editor_factory import BasicEditorFactory
#============= local library imports  ==========================


class _TextTableEditor(Editor):
    _pv = None
    _pc = None
    clear = Event
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

#        parent.addStretch(1)
#        parent.addWidget(self.control)

    def _on_clear(self):
        pass
#        if self.control:
#            self.control.clear()

    def update_editor(self, *args, **kw):
        '''
        '''
        adapter = self.factory.adapter
        tables = adapter.make_tables(self.value)
        for ti, border in tables:
            self._add_table(ti, border)
#        self.control.moveCursor(QTextCursor.Start)
#        self.control.ensureCursorVisible()
    def _add_table(self, tab, border):
        cursor = QTextCursor(self.control.textCursor())

        fmt = QTextTableFormat()
#        if self.factory.header_color:
#            br = fmt.borderBrush()
#
# #            br = QBrush()
# #            br.setColor(QColor(self.factory.header_color))
#            br.setColor(QColor('green'))
#            fmt.setBorderBrush(br)
#        fmt.setBorder(3)
#            fmt.setBorderBrush(br)

#        fmt.setBackground(br)
        fmt.setCellSpacing(0)
        fmt.setCellPadding(3)
        if border:
            fmt.setBorderStyle(QTextFrameFormat.BorderStyle_Solid)
        else:
            fmt.setBorderStyle(QTextFrameFormat.BorderStyle_None)

        cursor.insertTable(tab.rows(), tab.cols(), fmt)
        table = cursor.currentTable()
        ec = self.factory.even_color
        oc = self.factory.odd_color

        for ri, row in enumerate(tab.items):
            for ci, cell in enumerate(row.cells):
                tcell = table.cellAt(ri, ci)
                fmt = QTextTableCellFormat()

                if row.color:
                    c = row.color
                elif ri == 0:
                    c = self.factory.header_color
                else:
                    if (ri - 1) % 2 == 0:
                        c = ec
                    else:
                        c = oc

                if c:
                    fmt.setBackground(QColor(c))

                if cell.bold:
                    fmt.setFontWeight(QFont.Bold)
                else:
                    fmt.setFontWeight(QFont.Normal)

                fmt.setFontPointSize(10)
                tcell.setFormat(fmt)
                cur = tcell.firstCursorPosition()
                cur.insertText(cell.text)

#        self.control.setHtml(self.control.toHtml())

#
#        cols = self.factory.adapter.columns
#        if not isinstance(cols, int):
#            cols = len(cols)
#
#        cursor.insertTable(10, cols)
#
#        tab = cursor.currentTable()
#        fmt.setBorderStyle(QTextFrameFormat.BorderStyle_None)
# #        fmt.setHeight(1.25)
#
# #        print tab
#        for ri, item in enumerate(item_gen):
#            for ci, it in enumerate(item.items):
#                cell = tab.cellAt(ri, ci)
#                cur = cell.firstCursorPosition()
#                cur.insertText(it.text)
#
#
# #            pass
# #            print cursor
# #            cursor.MoveOperation(QTextCursor.NextRow)
# #            tab.insertRow()




#            ctrl.insertPlainText('{}\n'.format(item.text))


#        if self.value:
#            v, c, force = self.value
#            if force or v != self._pv or c != self._pc:
#                ctrl.setTextColor(c)
#                self._pc = c
#                self._pv = v

#        self.control.moveCursor(QTextCursor.End)
#        self.control.ensureCursorVisible()

class TextTableEditor(BasicEditorFactory):
    klass = _TextTableEditor
    bg_color = Color
    odd_color = Str
    even_color = Str
    header_color = Str
    clear = Str
    adapter = Any
#============= EOF =============================================
