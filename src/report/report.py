'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch

from reportlab.lib import colors
from src.report.autoupdate_parser import AutoupdateParser

PAGE_HEIGHT = defaultPageSize[1] 
PAGE_WIDTH = defaultPageSize[0]
styles = getSampleStyleSheet()

pageinfo = 'report'

from reportlab.platypus.flowables import Flowable, DocIf
class FlowableGraph(Flowable):
    def __init__(self, g, xoffset=0, size=None, fillcolor='red', strokcolor='black'):
        self.graph = g
        self.xoffset = xoffset
        if size is None:
            size = 6.0625 * inch
        self.size = size
        self.scale = size / (6 * inch)
    def wrap(self, *args):
        return (self.xoffset, self.size)
    def draw(self):
        canvas = self.canv
        canvas.translate(self.xoffset, 0)
        canvas.scale(self.scale, self.scale)
        self.graph.render_to_pdf(canvas=canvas, dest_box=(0, 0, self.size / inch, self.size / inch))


        
    
    
class Report:
    report_text = []
    def add_heading(self, h, i):
        p = Paragraph(h, styles[i])
        self.report_text.append(p)
    def add_spacer(self):
        self.report_text.append(Spacer(1, 0.2 * inch))
    def add_page_break(self):
        self.report_text.append(PageBreak())
    def add_paragraph(self, t):
        p = self._paragraph(t, 'Normal')
        self.report_text.append(p)
    def add_table(self, tdata, stylecmds):
        t = Table(tdata)
        ts = TableStyle(stylecmds)
        t.setStyle(ts)
        t.hAlign = 'LEFT'
        self.report_text.append(t)
    def add_graph(self, g):
        fg = FlowableGraph(g)
        self.report_text.append(fg)
    
    def _new_paragraph(self, t, s='Normal'):
        style = styles[s]
        p = Paragraph(t, style)
        return p

    def _draw_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 10)
        canvas.drawCentredString(PAGE_WIDTH / 2.0, 0.5 * inch, 'page %d ' % doc.page)
        canvas.restoreState()
    
    def _plusminus_sigma(self, n=1):
        s = unicode('\xb1{}'.format(n)) + unicode('\x73', encoding='Symbol')
        return s
    
    def create_cover_page(self, canvas, doc):
        #DRAW THE COVER PAGE
        #THIS SHOULD PROBABY EITHER NOT DO ANYTHING OR PRETTY PRINT PROJECT AND METADATA
        #PRINTS BRANDING INFO
#        nmgrllogo=Image(
#                        '/Users/Ross/ARLAB/images/NMGRLlogo.gif')
#        imp = '/Users/Ross/ARLAB/images/NMGRLlogo.gif'
#        canvas.drawInlineImage(imp, PAGE_WIDTH / 4.0, PAGE_HEIGHT / 2.0)


        author = 'Jake Ross'
        canvas.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT / 2.0 - .75 * inch, author)

        nmgrl = 'New Mexico Geochronology Research Laboratory'
        nmt = 'New Mexico Tech'
        canvas.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT / 2.0 - 1.5 * inch, nmgrl)
        canvas.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT / 2.0 - 1.8 * inch, nmt)

        import time
        fmt = '%B %d,%Y'
        date = time.strftime(fmt, time.gmtime())
        canvas.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT / 2.0 - 2.1 * inch, date)

        self._draw_footer(canvas, doc)
        #canvas.setFont('Times-Roman',9) 
        #canvas.drawString(inch, 0.75 * inch, "First Page / %s" % pageinfo) 
    def create_report_page(self, canvas, doc):
        self._draw_footer(canvas, doc)
        
    def _build_spectrum_table(self, tablen, samples):
        ar4039 = self._new_paragraph('<font size=9><super>40</super>Ar/<super>39</super>Ar</font>')
        ar3739 = self._new_paragraph('<font size=9><super>37</super>Ar/<super>39</super>Ar</font>')
        ar3639 = self._new_paragraph('<font size=9><super>36</super>Ar/<super>39</super>Ar</font>')
        ar39k = self._new_paragraph('<font size=9><super>39</super>Ar<sub>K</sub></font>')
        ar3639_mult = self._new_paragraph('<font size=7>(x 10<super>-3</super>)</font>')
        ar39k_mult = self._new_paragraph('<font size=7>(x 10<super>-15</super> mol)</font>')
        rad = self._new_paragraph('<font size=9><super>40</super>Ar*</font>')
        sigma = self._new_paragraph(self._plusminus_sigma())
        degrees = self._new_paragraph(unicode('(\xa1C)'))
        ar39 = self._new_paragraph('<font size=9><super>39</super>Ar</font>')
        
        title = self._new_paragraph('<font size=10 name="Helvetica-Bold">Table {}. <super>40</super>Ar/<super>39</super>Ar analytical data.</font>'.format(tablen))
        trows = [[title, ],
                 [],
                 ['', 'ID', 'Temp', ar4039 , ar3739, ar3639, ar39k, 'K/Ca', rad, ar39, 'Age', sigma],
                 ['', '', degrees, '', '', ar3639_mult, ar39k_mult, '', '(%)', '(%)', '(Ma)', '(Ma)'],
                 [],
#                 [info_line]
                 ]
        
        self.int_plat_age_rowids = []
        self.sample_rowids = []
        self.sample_ends = []
        for s in samples:
            self.sample_rowids.append(len(trows))
            self._build_sample_rows(trows, s)
            self.sample_ends.append(len(trows))
            
        ta = Table(trows)
        self._set_column_widths(ta)
        self._set_row_heights(ta)
        tblstyle = self._build_spectrum_table_style()
        ta.setStyle(tblstyle)
        
        return ta  
    
    def zap_orphans(self, trows, trip_row=38):
        s = len(trows) % trip_row
        if s < 2:
            self.sample_rowids[-1] += 1
            trows.insert(-1, [])
            if not s:
                self.sample_rowids[-1] += 1
                trows.insert(-1, [])
        
    def _build_sample_rows(self, trows, sample):  
        info_line = self._new_paragraph(u'<font size=9><b>{sample}</b></font>, <font size=7>{material}, {weight} mg, J={j}\xb1{jer}%, D={d}\xb1{der}, {irrad}, Lab#={l_number}</font>'.format(**sample.info))
        trows.append(['', info_line])
        
        for i, a in enumerate(sample.analyses):
            if i < 1:
                self.zap_orphans(trows)
                
            trows.append(a.get_data())
                
        intage_label = self._new_paragraph(u'<font size=9><b>Integrated age ' + self._plusminus_sigma(2) + '</b></font>')
        intage, intage_err = sample.get_isotopic_recombination_age()
        platage_label = self._new_paragraph(u'<font size=9><b>Plateau ' + self._plusminus_sigma(2) + '</b></font>')
        
        
        tot39 = '{:0.1f}'.format(sample.get_total39())
        kca, _er = sample.get_kca()
        kca = '{:0.1f}'.format(kca)
        
        nsteps = 'n={}'.format(sample.get_nsteps())
        args = sample.get_plateau_steps()
        if args:
            ptot39 = '{:0.1f}'.format(sample.get_total39(plateau=True))
            mswd = '{:0.2f}'.format(sample.get_mswd())
            ps, pe, pss = args 
            psteps = 'steps {}-{}'.format(ps, pe)
            npsteps = 'n={}'.format(pss)
            plat39 = '{:0.1f}'.format(sample.get_plateau_percent39())
            age, err = map('{:0.3f}'.format, sample.get_plateau_age())
            kca_args = sample.get_kca(plateau=True)
            pkca = self._new_paragraph(u'<font size=9>{:0.2f}\xb1{:0.2f}</font>'.format(*kca_args))
        else:
            ptot39 = ''
            mswd = ''
            psteps = ''
            npsteps = ''
            plat39 = ''
            age = ''
            err = ''
            kca = ''
            pkca = ''
        
        self.int_plat_age_rowids.append(len(trows))
        trows.append(['', intage_label, '', '', nsteps, '', tot39, kca, '', '', '{:0.2f}'.format(intage), '{:0.2f}'.format(intage_err)])
        
        n = len(sample.analyses)
        self.zap_widows(trows, n)

        trows.append(['', platage_label, '', psteps, npsteps, mswd, ptot39, pkca, '', plat39, age, err])
        trows.append([])
        
    def zap_widows(self, trows, n, trip_row=38, widow_rows=2):
        s = len(trows) % trip_row
        if s <= widow_rows:
            for i in range(n + widow_rows - s):
                trows.insert(-n - 2, [])
                self.sample_rowids[-1] += 1
                self.int_plat_age_rowids[-1] += 1
        
    def _build_spectrum_table_style(self):
        tblstyle = TableStyle([
                               ('SPAN', (0, 0), (-1, 0)),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('FONTSIZE', (0, 0), (-1, -1), 9),
                               ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                               ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
                               ('LINEBELOW', (0, 1), (-1, 1), 1, colors.black),
#                            ('ALIGN', (2, 0), (2, 0), 'LEFT'),
                               ('LINEBELOW', (0, 3), (-1, 3), 1.5, colors.black),
                               #('LINEBELOW', (0, 0), (-1, -1), 1, colors.red),
                               
#                               ('LINEBEFORE', (0, 0), (-1, -1), 1, colors.black),
                               ('ALIGN', (2, 0), (-1, -1), 'CENTER')
                              ])
        
        for ir in self.int_plat_age_rowids:
            tblstyle.add('SPAN', (1, ir), (3, ir))
            tblstyle.add('SPAN', (1, ir + 1), (2, ir + 1))
            
        for si in self.sample_rowids:
            tblstyle.add('SPAN', (1, si), (-1, si))
            
        return tblstyle
    
    def _set_row_heights(self, ta):
        ta._argH[1] = 0.0125 * inch
        ta._argH[4] = 0.2 * inch
        
        for s in self.sample_ends:
            try:
                ta._argH[s] = 0.25 * inch
            except IndexError:
                break
            
            
    def _set_column_widths(self, ta):
        ta._argW[0] = 0.17 * inch
        ta._argW[2] = 0.5 * inch
        st = 3
        ta._argW[st] = 0.6 * inch
        ta._argW[st + 1] = 0.6 * inch
        ta._argW[st + 2] = 0.6 * inch
        ta._argW[st + 3] = 0.7 * inch
        ta._argW[st + 4] = 0.5 * inch
        ta._argW[st + 5] = 0.5 * inch
        
    def create_report(self, p):
        doc = SimpleDocTemplate(p)
        _style = styles["Normal"]
        space = Spacer(1, 0.2 * inch)

        report_text = []
        
#        report_text.append(PageBreak())
        #samples = [('AF-32', 'Groundmass Concentrate', 20.55, 0.01, 0.001, 1.0004, 0.1, 'NM-205G', '56879-01')]
        
        
        parser = AutoupdateParser()

        p = '/Users/Ross/Documents/Antarctica/MinnaBluff/data/test.csv'
        p = '/Users/Ross/Documents/Antarctica/MinnaBluff/data/af50.csv'
        p = '/Users/Ross/Documents/Antarctica/MinnaBluff/data/gm-06.csv'
        
        samples = parser.parse(p)
        ta = self._build_spectrum_table(1, samples)
        ta.hAlign = 'LEFT'
        
#        ta.split(PAGE_WIDTH, PAGE_HEIGHT)
#        report_text.append(space)
#        report_text.append(Spacer(3.0*inch,0))
        report_text.append(ta)    
#         

#        report_text = self.report_text
        doc.build(report_text,
                  #onFirstPage=self.create_cover_page, 
                  onLaterPages=self.create_report_page)
#        
#        for i in range(20): 
#            bogustext = ("This is Paragraph number %s.  " % i) *20 
#            p = Paragraph(bogustext, style) 
#            Story.append(p) 
#            Story.append(Spacer(1,0.2*inch)) 
#        doc.build(Story, onFirstPage=self.create_cover_page, onLaterPages=self.create_report_page) 
def time_recursive():
    r = Report()
#    r.recursive = True
    r.cover_text = 'This report was generated by Reporter by Jake Ross'
    r.create_report('phello2.pdf')

def time_non_recursive():
    r = Report()
#    r.recursive = False
    r.cover_text = 'This report was generated by Reporter by Jake Ross'
    r.create_report('phello2.pdf')
        
    
if __name__ == '__main__':
#    from timeit import Timer
#    t = Timer('time_recursive', 'from __main__ import time_recursive')
#    
#    n = 5
#    tr = t.timeit(n)
#    print 'time r', tr, tr / 5
#    
#    t = Timer('time_non_recursive', 'from __main__ import time_non_recursive')
#    tr = t.timeit(n)
#    print 'time nr', tr, tr / 5
    time_non_recursive()
