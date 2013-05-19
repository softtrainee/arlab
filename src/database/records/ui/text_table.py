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
from traits.api import HasTraits, Any, Instance, Event, List, on_trait_change, Callable
from src.helpers.formatting import floatfmt
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
    def _make_header_row(self):
        return HeaderRow(*[self._header_cell_factory(args)
                            for args in self.columns])
    def make_tables(self, value):
        return self._make_tables(value)

    def _make_tables(self, value):
        raise NotImplementedError

    def _cell_factory(self, obj, args):
        fmt = floatfmt
        if len(args) == 3:
            ci, li, fmt = args
        else:
            ci, li = args

        return TextCell(getattr(obj, li), format=fmt)

    def _header_cell_factory(self, args):
        if len(args) == 3:
            ci, _, _ = args
        else:
            ci, _ = args

        return TextCell(ci)

#============= EOF =============================================
