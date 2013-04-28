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
from traits.api import HasTraits, Any
#============= standard library imports ========================
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.platypus.tables import Table
from reportlab.lib.units import inch
from src.constants import PLUSMINUS, SIGMA
#============= local library imports  ==========================
STYLES = getSampleStyleSheet()

class PDFTable(HasTraits):

    add_title = True
    add_header = True
    number = 1

    def _new_paragraph(self, t, s='Normal'):
        style = STYLES[s]
        p = Paragraph(t, style)
        return p

    def _plusminus_sigma(self, n=1):
        s = self._plusminus(n) + SIGMA
        return s

    def _plusminus(self, n=1):
        return unicode('{}{}'.format(PLUSMINUS, n))

    def zap_orphans(self, trows, trip_row=38):
        s = len(trows) % trip_row
        if s < 2:
            self.sample_rowids[-1] += 1
            trows.insert(-1, [])
            if not s:
                self.sample_rowids[-1] += 1
                trows.insert(-1, [])

#    def floatfmt(self, v, n=5, scale=1):
#        fmt = '{{:0.{}f}}'.format(n)
#        nv = fmt.format(v / scale)
#        if len(nv)>n+2:

    def _make(self, rows):
        ta = Table(rows)
        ta.hAlign = 'LEFT'
        self._set_column_widths(ta)
        self._set_row_heights(ta, rows)

        s = self._get_style(rows)
        ta.setStyle(s)
        return ta

    def _get_idxs(self, rows, klass):
            return [(i, v) for i, v in enumerate(rows)
                      if isinstance(v, klass)]
    def _set_column_widths(self, ta):
        ta._argW[0] = 0.17 * inch
#        ta._argW[2] = 0.5 * inch

    def _set_row_heights(self, ta, rows):
        pass


    def _get_style(self, rows):
        pass

from traits.api import Either, Str, Callable, List, Int

class Row(HasTraits):
    items = List
    fontsize = Int
    fontname = Str
    spans = List
    def render(self):
        return [it.render() for it in self.items]

    def add_item(self, span=1, **kw):
        if 'fontsize' not in kw and self.fontsize:
            kw['fontsize'] = self.fontsize

        self.items.append(RowItem(**kw))
        ss = len(self.items) - 1
        if span > 1:
            se = ss + span
            self.spans.append((ss, se))
            self.add_blank_item(span)
        elif span == -1:
            self.spans.append((ss, -1))

    def add_blank_item(self, n=1):
        for _ in range(n):
            self.add_item(value='')

    def __iter__(self):
        return (it.render() for it in self.items)

def Superscript(v):
    return '<super>{}</super>'.format(v)

def Subscript(v):
    return '<sub>{}</sub>'.format(v)

class BaseItem(HasTraits):
    value = Any
    fmt = Either(Str, Callable)
    fontsize = Int(8)
    fontname = 'Helvetica'
    def render(self):
        v = self.value
        if not isinstance(v, Paragraph):
            fmt = self.fmt
            if fmt is None:
                fmt = u'{}'
            if isinstance(fmt, (str, unicode)):
                v = fmt.format(v)
            else:
                v = fmt(v)

        v = self._set_font(v, self.fontsize, self.fontname)

        return v

    def _set_font(self, v, size, name):
        if isinstance(v, Paragraph):
            for frag in v.frags:
                frag.fontName = name
                if frag.super or frag.sub:
                    frag.fontSize = size - 2
                else:
                    frag.fontSize = size
        else:
            v = self._new_paragraph(u'<font size={} name="{}">{}</font>'.format(size, name, v))

        return v

    def _new_paragraph(self, t, s='Normal'):
        style = STYLES[s]
        p = Paragraph(t, style)
        return p

class SummaryRow(Row):
    pass
class AnalysisRow(Row):
    pass
class FootNoteRow(Row):
    pass
class FooterRow(Row):
    pass

class Title(Row):
    fontname = 'Helvetica-bold'
    def __init__(self, value='', **kw):
        super(Title, self).__init__(**kw)
        self.add_item(value=value, **kw)
    def __iter__(self):
        return (self.render() for i in (1,))

class RowItem(BaseItem):
    pass

def NamedParameter(name, value):
    return '<b>{}</b>: {}'.format(name, value)

def Anchor(tagname, num, s='Normal'):
    snum = Superscript(num)
    link = '{{}}<a href="#{}" color="green">{}</a>'.format(tagname, snum)
    tag = '{{}}{}: {{}}<a name="{}"/>'.format(snum, tagname)

    style = STYLES[s]

    p1 = lambda x: Paragraph(link.format(x), style)
    p2 = lambda n, v: Paragraph(tag.format(n, v), style)

    return p1, p2


#============= EOF =============================================
