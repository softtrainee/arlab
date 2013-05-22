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
from traits.api import HasTraits, Any, Instance, Event, List, on_trait_change, Callable, Bool
from src.helpers.formatting import floatfmt
from src.constants import PLUSMINUS
#============= standard library imports ========================
#============= local library imports  ==========================
# def fixed_width(m, i):
#    return '{{:<{}s}}'.format(i).format(m)
# def floatfmt(m, i=6):
#    if abs(m) < 10 ** -i:
#        return '{:0.2e}'.format(m)
#    else:
#        return '{{:0.{}f}}'.format(i).format(m)

class TextCell(HasTraits):
    text = ''
    color = 'black'
    bg_color = None
    bold = False
    format = Callable
    def __init__(self, text, *args, **kw):
        super(TextCell, self).__init__(**kw)

        if self.format:
            self.text = self.format(text)
        else:
            self.text = str(text)

#        for k in kw:
#            setattr(self, k, kw[k])
class BoldCell(TextCell):
    bold = True

class TextRow(HasTraits):
    cells = List
    color = None
    def __init__(self, *args, **kw):
        super(TextRow, self).__init__(**kw)
        self.cells = list(args)

class HeaderRow(TextRow):
    @on_trait_change('cells[]')
    def _update_cell(self):
        for ci in self.cells:
            ci.bold = True

class TextTable(HasTraits):
    items = List
    border = Bool
    def __init__(self, *args, **kw):
        self.items = list(args)
        super(TextTable, self).__init__(**kw)
    def rows(self):
        return len(self.items)

    def cols(self):
        return max([len(ri.cells) for ri in self.items])

class TextTableAdapter(HasTraits):
#    def __getattr__(self, attr):
#        pass
    columns = List
    _cached_table = None
    def _make_header_row(self):
        return HeaderRow(*[self._header_cell_factory(args)
                            for args in self.columns])

    def make_tables(self, value):
        return self._make_tables(value)
#        if not self._cached_table:
#            table = self._make_tables(value)
#            self._cached_table = table[0]
#        else:
#            for i, vi in enumerate(value):
#                for ci, args in enumerate(self.columns):
#                    if len(args) == 3:
#                        fmt = args[2]
#                    else:
#                        fmt = floatfmt
#                    try:
#                        self._cached_table.items[i + 1].cells[ci].text = fmt(getattr(vi, args[1]))
#                    except IndexError:
#                        self._cached_table.items.append(TextRow(*[self._cell_factory(vi, args)
#                                                                  for args in self.columns]))
#        return [self._cached_table]

    def _make_tables(self, value):
        raise NotImplementedError

    def _cell_factory(self, obj, args):
        fmt = floatfmt
        if len(args) == 3:
            _, li, fmt = args
        else:
            _, li = args

        return TextCell(getattr(obj, li), format=fmt)

    def _header_cell_factory(self, args):
        if len(args) == 3:
            ci, _, _ = args
        else:
            ci, _ = args

        return TextCell(ci)

class SimpleTextTableAdapter(TextTableAdapter):

    def _make_tables(self, value):
        return [self._make_signal_table(value)]

    def _make_signal_table(self, sg):
        rs = [self._make_header_row()]
        rs.extend(
                   [TextRow(*[self._cell_factory(ri, args)
                              for args in self.columns])
                                for ri in sg]
                   )
        tt = TextTable(border=True,
                       *rs
                       )
        return tt

class ValueErrorAdapter(TextTableAdapter):
    columns = [
               ('', 'name', str),
               ('Value', 'value'),
               (u'{}1s'.format(PLUSMINUS), 'error'),
               ]

    def _make_tables(self, value):
        rs = [self._make_header_row(),
              ]
        for vi in value:
            ri = TextRow(
                         self._cell_factory(vi, (None, 'name', str)),
                         self._cell_factory(vi, (None, 'value')),
                         self._cell_factory(vi, (None, 'error')),
                         )
            rs.append(ri)
        tt = TextTable(border=True, *rs)
        return [tt]

class RatiosAdapter(ValueErrorAdapter):
    columns = [
               ('Ratio', 'name', str),
               ('Value', 'value'),
               (u'{}1s'.format(PLUSMINUS), 'error'),
               ]


#============= EOF =============================================
