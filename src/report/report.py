
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch

#from reportlab.lib import colors

PAGE_HEIGHT = defaultPageSize[1]; PAGE_WIDTH = defaultPageSize[0]
styles = getSampleStyleSheet()

pageinfo = 'report'

from reportlab.platypus.flowables import Flowable
class FlowableGraph(Flowable):
    def __init__(self, g, xoffset = 0, size = None, fillcolor = 'red', strokcolor = 'black'):
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
        self.graph.render_to_pdf(canvas = canvas, dest_box = (0, 0, self.size / inch, self.size / inch))


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
    def _paragraph(self, t, s):
        style = styles[s]
        p = Paragraph(t, style)
        return p

    def _draw_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 10)
        canvas.drawCentredString(PAGE_WIDTH / 2.0, 0.5 * inch, 'page %d ' % doc.page)
        canvas.restoreState()
    def create_cover_page(self, canvas, doc):
        #DRAW THE COVER PAGE
        #THIS SHOULD PROBABY EITHER NOT DO ANYTHING OR PRETTY PRINT PROJECT AND METADATA
        #PRINTS BRANDING INFO
#        nmgrllogo=Image(
#                        '/Users/Ross/ARLAB/images/NMGRLlogo.gif')
        imp = '/Users/Ross/ARLAB/images/NMGRLlogo.gif'
        canvas.drawInlineImage(imp, PAGE_WIDTH / 4.0, PAGE_HEIGHT / 2.0)


        author = 'Jake Ross'
        canvas.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT / 2.0 - .75 * inch, author)

        nmgrl = 'New Mexico Geochronology Research Laboratory'
        nmt = 'New Mexico Tech'
        canvas.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT / 2.0 - 1.5 * inch, nmgrl)
        canvas.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT / 2.0 - 1.8 * inch, nmt)

        import time
        format = '%B %d,%Y'
        date = time.strftime(format, time.gmtime())
        canvas.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT / 2.0 - 2.1 * inch, date)

        self._draw_footer(canvas, doc)
        #canvas.setFont('Times-Roman',9) 
        #canvas.drawString(inch, 0.75 * inch, "First Page / %s" % pageinfo) 
    def create_report_page(self, canvas, doc):


        self._draw_footer(canvas, doc)
    def create_report(self, p):
        doc = SimpleDocTemplate(p)
        _style = styles["Normal"]
#        space = Spacer(1,0.2*inch)

        #report_text=[]
        #report_text.append(PageBreak())
#        for i in range(1):
#            headertext=Paragraph(('this is a header'),style)
#            report_text.append(headertext)
#            report_text.append(space)
#        
#        from numpy import random
#        tdata=[['L#','Sample','Age','Error(2s)']]
#        for i in range(30):
#            
#            t=[1000+i,'SMP-0%i'%i,'%0.3f'%random.random(),'%0.3f'%(random.random()/100.0)]
#            tdata.append(t)
#        ta=Table(tdata,
#                 colWidths=[0.5*inch,1.5*inch,1*inch,1*inch],rowHeights=[0.25*inch]*len(tdata))
#        tblstyle=TableStyle([('BACKGROUND',(0,3),(-1,3),colors.blue),
#                             ('TEXTCOLOR',(0,0),(-1,-1),colors.black),
#                             ('LINEBELOW',(0,0),(-1,0),2,colors.black),
#                             # ('LINEBEFORE',(1,1),(-1,-1),1,colors.black),
#                             
#                             
#                             ('LINEBELOW',(0,1),(-1,-2),1,colors.black),
#                              ('LINEBEFORE',(1,1),(-1,-1),1,colors.black),
#                              ])
#        ta.setStyle(tblstyle)
#        ta.hAlign='LEFT'
#        report_text.append(space)
#        report_text.append(Spacer(3.0*inch,0))
#        report_text.append(ta)    
#         
        report_text = self.report_text
        doc.build(report_text, onFirstPage = self.create_cover_page, onLaterPages = self.create_report_page)
#        
#        for i in range(20): 
#            bogustext = ("This is Paragraph number %s.  " % i) *20 
#            p = Paragraph(bogustext, style) 
#            Story.append(p) 
#            Story.append(Spacer(1,0.2*inch)) 
#        doc.build(Story, onFirstPage=self.create_cover_page, onLaterPages=self.create_report_page) 
if __name__ == '__main__':
    r = Report()
    r.cover_text = 'This report was generated by Reporter by Jake Ross'
    r.create_report('phello2.pdf')

