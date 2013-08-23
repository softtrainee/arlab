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
# from traits.api import HasTraits, List
# from traitsui.api import View, Item
#============= standard library imports ========================
from reportlab.platypus.tables import Table, TableStyle
# from reportlab.platypus.flowables import PageBreak, Flowable
from reportlab.platypus.doctemplate import BaseDocTemplate, \
    PageTemplate, FrameBreak
# from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm, inch
from reportlab.lib import colors
from reportlab.platypus.frames import Frame

# from chaco.pdf_graphics_context import PdfPlotGraphicsContext
#============= local library imports  ==========================
from src.loggable import Loggable
from src.experiment.loading.component_flowable import ComponentFlowable
from src.canvas.canvas2D.scene.primitives.primitives import LoadIndicator
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.flowables import Spacer

STYLES = getSampleStyleSheet()
class LoadingPDFWriter(Loggable):
    def build(self, path, positions, component, meta):
        self.info('saving load to {}'.format(path))
        doc = BaseDocTemplate(path,
                                  leftMargin=0.25 * inch,
                                  rightMargin=0.25 * inch,
                                  topMargin=0.25 * inch,
                                  bottomMargin=0.25 * inch
#                                   _pageBreakQuick=0,
#                                   showBoundary=1
                                  )
#             doc = SimpleDocTemplate(path)



        n = len(positions)
        idx = int(round(n / 2.))

        p1 = positions[:idx]
        p2 = positions[idx:]
#
        m = self._make_meta_table(meta)
        t1 = self._make_table(p1)
        t2 = self._make_table(p2)

        t3 = self._make_footnotes_table(component)
        t3.hAlign = 'LEFT'

        fl = [
              m,
              Spacer(0, 5 * mm),
              ComponentFlowable(component=component,
                                hAlign='CENTER'
                                ),
              FrameBreak(),
              Spacer(0, 5 * mm),
              t1,
              FrameBreak(),
              Spacer(0, 5 * mm),
              t2,
              FrameBreak(),
              t3
              ]

        # make 3 frames top, lower-left, lower-right
        lm = doc.leftMargin
        bm = doc.bottomMargin + doc.height * .333

        fw = doc.width
        fh = doc.height * 0.666
        top = Frame(lm, bm, fw, fh)

        fw = doc.width / 2.
        fh = doc.height * 0.333
        bm = doc.bottomMargin
        lbottom = Frame(lm, bm, fw, fh)
        rbottom = Frame(lm + doc.width / 2., bm, fw, fh)

        template = PageTemplate(frames=[top, lbottom, rbottom])
        doc.addPageTemplates(template)

        doc.build(fl)

    def _make_meta_table(self, meta):
#         p = Paragraph()
        items = '<b>Load:</b> {load_name}|<b>Loader</b>: {username}|<b>Date</b>: {load_date}'.format(**meta).split('|')
        row1 = [Paragraph(ti, STYLES['Normal']) for ti in items]

        items = '<b>Projects</b>: {projects} | | '.format(**meta).split('|')
        row2 = [Paragraph(ti, STYLES['Normal']) for ti in items]

        data = [row1, row2]
        table = Table(data, hAlign='LEFT')
        return table

    def _make_footnotes_table(self, canvas):
        data = [('L#', 'Holes', 'Weight', 'Note')]
#         man = self.manager

        ts = TableStyle()
        ts.add('LINEBELOW', (0, 0), (-1, 0), 1, colors.black)

        ts.add('FONTSIZE', (-3, 1), (-1, -1), 8)
        ts.add('VALIGN', (-3, 1), (-1, -1), 'MIDDLE')
#         positions = positions * 15
        idx = 0
        for pi in sorted(canvas.scene.get_items(LoadIndicator),
                         key=lambda x: x.name):

#         for pi in positions:
            if pi.note or pi.weight is not None:
                row = (pi.labnumber_label.text,
                       pi.name,
                       pi.weight, pi.note)
                data.append(row)
                if idx % 2 == 0:
                    ts.add('BACKGROUND', (0, idx + 1), (-1, idx + 1),
                            colors.lightgrey)
                idx += 1

        cw = map(lambda x: mm * x, [12, 20, 22, 125])

        rh = [mm * 5 for _ in range(len(data))]
        t = Table(data,
                  colWidths=cw,
                  rowHeights=rh
                  )

        t.setStyle(ts)


        return t

    def _make_table(self, positions):
        data = [('L#', 'Irradiation', 'Sample', 'Positions')]
#         man = self.manager

        ts = TableStyle()
        ts.add('LINEBELOW', (0, 0), (-1, 0), 1, colors.black)

        ts.add('FONTSIZE', (-3, 1), (-1, -1), 8)
        ts.add('VALIGN', (-3, 1), (-1, -1), 'MIDDLE')
#         positions = positions * 15

        for idx, pi in enumerate(positions):
            row = (pi.labnumber, pi.irradiation_str, pi.sample,
                   pi.position_str)
            data.append(row)
            if idx % 2 == 0:
                ts.add('BACKGROUND', (0, idx + 1), (-1, idx + 1),
                        colors.lightgrey)

        cw = map(lambda x: mm * x, [12, 20, 22, 50])

        rh = [mm * 5 for i in range(len(data))]
        t = Table(data,
                  colWidths=cw,
                  rowHeights=rh
                  )

        t.setStyle(ts)

        return t
#============= EOF =============================================
