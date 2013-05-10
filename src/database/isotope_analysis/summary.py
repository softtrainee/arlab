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
from traits.api import HasTraits, Any, Instance
from traitsui.api import View, Item
# from src.displays.rich_text_display import RichTextDisplay
# from pyface.timer.do_later import do_later
import math
from src.displays.display import  DisplayController
#============= standard library imports ========================
#============= local library imports  ==========================
# def fixed_width(m, i):
#    return '{{:<{}s}}'.format(i).format(m)
# def floatfmt(m, i=6):
#    if abs(m) < 10 ** -i:
#        return '{:0.2e}'.format(m)
#    else:
#        return '{{:0.{}f}}'.format(i).format(m)
class Summary(HasTraits):
    display = Instance(DisplayController)
    record = Any


    @classmethod
    def fixed_width(cls, m, i):
        return '{{:<{}s}}'.format(i).format(m)

    @classmethod
    def calc_percent_error(cls, v, e):
        try:
            sigpee = '{:0.2f}%'.format(abs(e / v * 100))
        except ZeroDivisionError:
            sigpee = 'NaN'
        return sigpee

    @classmethod
    def make_error(cls, v, e):
        return '{} ({})'.format(cls.floatfmt(e), cls.calc_percent_error(v, e))

#    @classmethod
#    def floatfmt(cls, m, i=6):
#        if not m:
#            return '0.0'
#
#        if abs(m) < 10 ** -i:
#            return '{:0.2e}'.format(m)
#        else:
#            return '{{:0.{}f}}'.format(i).format(m)

    @classmethod
    def floatfmt(cls, f, n=6):
        if not f:
            return '0.0'
        if abs(f) < math.pow(10, -(n - 1)) or abs(f) > math.pow(10, n):
            fmt = '{:0.2e}'
        else:
            fmt = '{{:0.{}f}}'.format(n)

        return fmt.format(f)
#    def __init__(self, *args, **kw):
#        super(Summary, self).__init__(*args, **kw)
#        self.refresh()

    def refresh(self):
        self.build_summary()

    def build_summary(self, *args, **kw):
        self.display.clear(gui=False)
        self._build_summary()
#        def do():
#
#            #d.freeze()
#
#            #double clear for safety
#            #d.clear(gui=False)
#            self._build_summary(*args, **kw)
#            #d.thaw()


    def add_text(self, *args, **kw):
        self.display.add_text(gui=False, *args, **kw)

    def _make_keyword(self, name, value, new_line=False, underline=0, width=20):
        value = str(value)

        name = '{}= '.format(name)
        self.add_text(name, new_line=False, bold=True, underline=underline)

        if not underline:
            self.add_text(self.fixed_width(value, max(0, width - len(name))),
                          new_line=new_line)
        else:
            self.add_text(self.fixed_width(value, max(0, underline - len(name))),
                          new_line=new_line, underline=True)

    def _build_summary(self, *args, **kw):
        pass

    def _display_default(self):
        return DisplayController(default_size=12,
                               width=self.record.item_width - 10,
#                               selectable=True,
#                               default_color='black',
#                               scroll_to_bottom=False,
                               font_name='courier'
#                               font_name='Bitstream Vera Sans Mono'
#                               font_name='monospace'
                               )
    def traits_view(self):
        v = View(
                 Item('display',
#                      height=0.8,
                      show_label=False, style='custom'),
                 )
        return v
#============= EOF =============================================
