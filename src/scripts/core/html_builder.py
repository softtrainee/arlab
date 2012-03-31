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
from traits.api import HasTraits, String
from traitsui.api import View, Item, HTMLEditor
class Table(object):
    def __init__(self, attribs=None):
        super(Table, self).__init__()
        self.rows = []

        self.attribs = attribs

    def add_row(self, cells):
        tr = TableRow()
        for c in cells:
            tr.cells.append(TableCell(c))
        self.rows.append(tr)

    def __str__(self):
        rs = ''
        stag = '<table %s>' % self.attribs if self.attribs else '<table>'
        stag += '\n'
        for r in self.rows:
            rs += str(r)

        return '%s%s</table>\n' % (stag, rs)

class TableRow(object):
    def __init__(self, **kw):
        super(TableRow, self).__init__()
        self.cells = []

    def __str__(self):
        tc = ''
        for c in self.cells:
            tc += str(c)
        return '\t<tr>\n%s\t</tr>\n' % tc

class TableCell(object):
    def __init__(self, value):
        super(TableCell, self).__init__()
        self.value = value
#        self.font=font
#        self.size=size
    def __str__(self):
        v = self.value
#        if self.font is not None:
#            v='<font face="%s">%s</font>'%(self.font,self.value)
#            if self.size is not None:
#                v='<font face="%s" size="%s">%s</font>'%(self.font,self.size,self.value)

        return '\t\t<td>%s</td>\n' % v

class HTMLDoc(object):
    def __init__(self, attribs=None):
        super(HTMLDoc, self).__init__()
        self.attribs = attribs
        self.elements = []

    def add_text(self, t):
        self.elements.append(t + '<br />')

    def add_table(self, **kw):
        t = Table(**kw)
        self.elements.append(t)
        return t

    def add_list(self, items=None, kind='unordered'):
        lklass = HTMLList
        if kind == 'ordered':
            lklass = HTMLOList

        l = lklass()
        if items is not None:
            for i in items:
                l.add_item(HTMLListItem(i))
        self.elements.append(l)
        return l

    def __str__(self):

        stag = '<body %s>' % self.attribs if self.attribs else '<body>'
        stag += '\n'
        s = ''
        for element in self.elements:
            s += str(element)
        p = '%s%s</body>' % (stag, s)
        print p
        return p

    def add_heading(self, h, **kw):
        h = HTMLText(h, **kw)
        self.elements.append(h)

class HTMLText(object):
    def __init__(self, value, heading=None, size=None, color=None, face=None):
        super(HTMLText, self).__init__()
        self.value = value
        self.color = color
        self.face = face
        self.size = size
        self.heading = heading

    def __str__(self):
        f = '<font '
        for a in ['face', 'color', 'size']:
            at = getattr(self, a)
            if at is not None:
                f += '%s="%s" ' % (a, at)
        if f == '<font ':
            f = str(self.value)
        else:
            f += '>' + self.value + '</font>'

        if self.heading is not None:
            f = '<h%i>%s</h%i>\n' % (self.heading, f, self.heading)
        return f

class HTMLList(object):
    tag = 'ul'
    def __init__(self):
        super(HTMLList, self).__init__()
        self.items = []
    def add_item(self, a):
        self.items.append(a)

    def __str__(self):
        ii = ''
        for i in self.items:
            ii += str(i)
        return '<%s>\n%s</%s\n>' % (self.tag, ii, self.tag)

class HTMLOList(HTMLList):
    tag = 'ol'

class HTMLListItem(object):
    def __init__(self, value):
        super(HTMLListItem, self).__init__()
        self.value = value

    def __str__(self):
        return '\t<li>%s</li>\n' % self.value

class DemoWindow(HasTraits):
    msg = String
    v = View(Item('msg', editor=HTMLEditor(),
                show_label=False),
           resizable=True,

           width=500,
           height=500
           )

if __name__ == '__main__':
    doc = HTMLDoc(attribs='bgcolor = "#ffffcc" text = "#000000"')
    doc.add_heading('Bakeout Documentation', heading=2, color='red')
    doc.add_heading('Parameters', heading=3)
    doc.add_text('Setpoint (C), Duration (min)')
    doc.add_list(['Setpoint (C) -- Bakeout Controller Setpoint',
                  'Duration (min) -- Heating duration'
                  ])
    table = doc.add_table(attribs='bgcolor="#D3D3D3" width="90%"')
    r1 = HTMLText('Ex.', face='courier', size='2')
    table.add_row([r1])

    r2 = HTMLText('150,360', face='courier', size='2')
    table.add_row([r2])
    print doc
    dem = DemoWindow(msg=str(doc))
    dem.configure_traits()
