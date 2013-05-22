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
from traits.api import HasTraits, Event, Color, Str, Any, Int
from traitsui.api import View, Item
from traitsui.qt4.editor import Editor
#============= standard library imports ========================
from PySide.QtGui import QTextEdit, QPalette, QTextCursor, QTextTableFormat, QTextFrameFormat, \
    QTextTableCellFormat, QBrush, QColor, QFont, QPlainTextEdit, QTextCharFormat
from traitsui.basic_editor_factory import BasicEditorFactory
import time
from src.simple_timeit import timethis
#============= local library imports  ==========================


class _TextTableEditor(Editor):
    _pv = None
    _pc = None
    clear = Event
    refresh = Event
    control_klass=QTextEdit
    def init(self, parent):
        '''

        '''
        if self.control is None:
            self.control = self.control_klass()

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
        tables=adapter.make_tables(self.value)
        for ti in tables:
            self._add_table(ti)
            
#            timethis(self._add_table, args=(ti,), msg='add_table')
#            timethis(self._add_table, args=(ti,), msg='add_table')
    
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
                cur=tcell.firstCursorPosition()
                
                cur.insertText(cell.text, cell_fmt)
                    
        
        
class _FastTextTableEditor(_TextTableEditor):
    control_klass=QPlainTextEdit
    def _add_table(self,tab):
#        cell_fmt = QTextTableCellFormat()
#        cell_fmt.setFontPointSize(10)
        fmt=QTextCharFormat()
        fmt.setFont(QFont('consolas'))
        fmt.setFontPointSize(self.factory.font_size)
        cursor = QTextCursor(self.control.textCursor())
        bc = QColor(self.factory.bg_color) if self.factory.bg_color else None
        ec,oc,hc=bc,bc,bc
        if self.factory.even_color:
            ec = QColor(self.factory.even_color)
        if self.factory.odd_color:
            oc = QColor(self.factory.odd_color)
        if self.factory.header_color:
            hc = QColor(self.factory.header_color)
            
        for i,row in enumerate(tab.items):
            cell=row.cells[0]
            if cell.bold:
                fmt.setFontWeight(QFont.Bold)
            else:
                fmt.setFontWeight(QFont.Normal)
            
            if i==0 and hc:
                c=hc
            elif (i-1)%2==0:
                c=ec
            else:
                c=oc
            if c:
                fmt.setBackground(c)
            
            txt=''.join(['{{:<{}s}}'.format(cell.width).format(cell.text)
                          for cell in row.cells
                          ]) 
#            for i,cell in enumerate(row.cells):
#                txt='
#                if i==n-1:
#                    txt=txt+'\n'
            
            cursor.insertText(txt+'\n', fmt)
        cursor.insertText('\n')
#        for ri, row in enumerate(tab.items):
#            c = bc
#            if row.color:
#                c = QColor(row.color)
#            elif ri == 0:
#                c = hc
#            else:
#                if (ri - 1) % 2 == 0:
#                    c = ec
#                else:
#                    c = oc
#            if c:
#                cell_fmt.setBackground(c)
#            rt=
            
#            for ci, cell in enumerate(row.cells):
#                if cell.bg_color:
#                    cell_fmt.setBackground(QColor(cell.bg_color))
#                if cell.bold:
#                    cell_fmt.setFontWeight(QFont.Bold)
#                else:
#                    cell_fmt.setFontWeight(QFont.Normal)

#            tcell = table.cellAt(ri, ci)
#            cur=tcell.firstCursorPosition()
#            cur.insertText(cell.text, cell_fmt)
#        txt='\n'.join([[''.join(['{{:<{}s}}'.format(ci.width).format(ci.text) for ci in row.cells])]
#                        for row in tab.items]
#                      )
#        cursor.insertText(txt, fmt)
            
class TextTableEditor(BasicEditorFactory):
    klass = _TextTableEditor
    bg_color = Color
    odd_color = Str
    even_color = Str
    header_color = Str
    clear = Str
    adapter = Any
    refresh = Str
    font_size=Int(12)
    
class FastTextTableEditor(TextTableEditor):
    klass = _FastTextTableEditor#_TextTableEditor
#============= EOF =============================================
