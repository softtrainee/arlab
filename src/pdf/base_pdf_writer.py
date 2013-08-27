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
#============= standard library imports ========================
from reportlab.platypus.doctemplate import BaseDocTemplate, PageTemplate
from reportlab.lib.units import inch
from reportlab.platypus.tables import Table, TableStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
#============= local library imports  ==========================
from src.loggable import Loggable
from reportlab.platypus.frames import Frame
from reportlab.platypus.flowables import Spacer
from reportlab.lib import colors
from src.pdf.items import Anchor
from reportlab.lib.pagesizes import landscape, letter

STYLES = getSampleStyleSheet()
class BasePDFWriter(Loggable):
    _footnotes = None
    orientation = 'portrait'
    def _new_base_doc_template(self, path):
        pagesize = letter
        if self.orientation == 'landscape':
            pagesize = landscape(letter)

        doc = BaseDocTemplate(path,
                              leftMargin=0.25 * inch,
                              rightMargin=0.25 * inch,
                              topMargin=0.25 * inch,
                              bottomMargin=0.25 * inch,
                              pagesize=pagesize
#                                   _pageBreakQuick=0,
#                                   showBoundary=1
                              )
        return doc

    def build(self, path, *args, **kw):
        self.info('saving pdf to {}'.format(path))
        doc = self._new_base_doc_template(path)
        flowables, templates = self._build(doc, *args, **kw)
        for ti in templates:
            doc.addPageTemplates(ti)

        doc.build(flowables)

    def _build(self, *args, **kw):
        raise NotImplementedError

    def _new_table(self, style, data, hAlign='LEFT', *args, **kw):
        t = Table(data, hAlign=hAlign, *args, **kw)
        t.setStyle(style)
        return t

    def _new_style(self, header_line_idx=None, header_line_width=1,
                   header_line_color='black'):

        ts = TableStyle()
        if isinstance(header_line_color, str):
            try:
                header_line_color = getattr(colors, header_line_color)
            except AttributeError:
                header_line_color = colors.black

        if header_line_idx is not None:
            ts.add('LINEBELOW', (0, header_line_idx),
                                (-1, header_line_idx),
                                header_line_width, header_line_color)

        return ts

    def _new_paragraph(self, t, s='Normal'):
        style = STYLES[s]
        p = Paragraph(t, style)
        return p

    def _default_frame(self, doc):
        return Frame(doc.leftMargin, doc.bottomMargin,
                     doc.width, doc.height)

    def _new_page_template(self, frames):
        temp = PageTemplate(frames=frames)
        return temp

    def _new_spacer(self, w, h):
        return Spacer(w * inch, h * inch)

    def _make_footnote(self, tagname, tagName, tagText, linkname, link_extra=None):
        if self._footnotes is None:
            self._footnotes = []

#         n = len(self._footnotes)
#         link, tag = Anchor('{}_{}'.format(tagname, id(self)), n + 1)
#         para = link(linkname, extra=link_extra)
#         self._footnotes.append(tag(tagName, tagText))
        return para
#============= EOF =============================================
