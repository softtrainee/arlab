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
from traits.api import HasTraits, Float, Property, Any, Instance
from traitsui.api import View, Item
#============= standard library imports ========================
#import wx
#============= local library imports  ==========================
#from src.database.isotope_analysis.selectable_readonly_texteditor import SelectableReadonlyTextEditor
from src.displays.rich_text_display import RichTextDisplay
#from src.data_processing.regression.regressor import Regressor

PLUSMINUS = unicode('\xb1')
PLUSMINUS_ERR = '{}Err.'.format(PLUSMINUS)
class AnalysisSummary(HasTraits):
    age = Float
    error = Float
    result = Any

    display = Instance(RichTextDisplay)
    def __init__(self, *args, **kw):
        super(AnalysisSummary, self).__init__(*args, **kw)
        self._build_summary()

    def _build_summary(self):
        d = self.display
        result = self.result

        isos = result.isos
        isos = sorted(isos, key=lambda k:int(k[2:]))
        isos.reverse()

        fits = result.fits
        intercepts = result.intercepts
        baselines = result.baselines
        if baselines is None:
            baselines = [(0, 0) for i in range(len(isos))]

        d.add_text('RID={} Labnumber={}'.format(result.rid, result.labnumber), bold=True)
        d.add_text('date={} time={}'.format(result.rundate, result.runtime), bold=True)

        floatfmt = lambda m, i = 5: '{{:0.{}f}}'.format(i).format(m)
        width = lambda m, i: '{{:<{}s}}'.format(i).format(m)

        #add header
        columns = [('Iso.', 5),
                   ('Int.', 12), (PLUSMINUS_ERR, 12),
                   ('Fit', 10),
                   ('Baseline', 12), (PLUSMINUS_ERR, 15),
                   ('Blank', 12), (PLUSMINUS_ERR, 12)
                   ]
        widths = [w for _, w in columns]

        msg = ''.join([width(m, w) for m, w in columns])
        d.add_text(msg, underline=True, bold=True)

        #add isotopes
        for i, iso in enumerate(isos):
            fit = fits[iso]
            try:
                inter, inter_err = intercepts[iso]
            except KeyError:
                inter, inter_err = 0, 0
            try:
                base, base_err = baselines[iso]
            except KeyError:
                base, base_err = 0, 0

            blank = 0
            blank_err = 0
            msgs = [
                    iso,
                    floatfmt(inter),
                    floatfmt(inter_err),
                    fit,
                    floatfmt(base),
                    floatfmt(base_err),
                    floatfmt(blank),
                    floatfmt(blank_err)
                    ]
            msg = ''.join([width(m, w) for m, w in zip(msgs, widths)])
#
            d.add_text(msg, underline=i == len(isos) - 1)

    def _display_default(self):
        return RichTextDisplay(default_size=12,
                               width=700,
                               selectable=True,
                               default_color='black')

    def traits_view(self):
        v = View(Item('display', show_label=False, style='custom'))
        return v


#============= EOF =============================================
#class AnalysisSummary2(HasTraits):
#    age = Float
#    error = Float
#    result = Any
#
#    summary = Property(depends_on='age,err')
#
#    header1 = ['ID', 'Date', 'Time']
#    header2 = ['Detector', 'Signal']
#
#    def _get_summary(self):
#        from jinja2 import Template
#        doc = '''
#{{header1}}
#{{data1}}
#
#Name:{{result.filename}}
#Root:{{result.directory}}
#
#{{header2}}
#{%- for k,v in signals %}
#{{k}}\t{{v}} 
#{%- endfor %}
#
#Age : {{obj.age}}\xb1{{obj.error}}    
#'''
#
#        data1 = map(lambda x: getattr(self.result, x), ['rid', 'rundate', 'runtime'])
#
#        temp = Template(doc)
#        join = lambda f, n: ('\t' * n).join(f)
##        join = '\t\t\t'.join
#        entab = lambda x:map('{}'.format, map(str, x))
#        makerow = lambda x, n: join(entab(x), n)
#        result = self.result
#        r = temp.render(result=result,
#                           header1=makerow(self.header1, 3),
#                           header2=makerow(self.header2, 1),
#                           data1=makerow(data1, 3),
#                           signals=zip(result.det_keys,
#                                       result.intercepts
#                                       ),
#                           obj=self,
#                           )
#        return r
#
#    def traits_view(self):
##        s = 51
#        ha1 = wx.TextAttr()
#        f = wx.Font(12, wx.MODERN, wx.NORMAL,
#                         wx.NORMAL, False, u'Consolas')
#        f.SetUnderlined(True)
#        ha1.SetFont(f)
#        ha1.SetTabs([200, ])
#
#        f.SetUnderlined(False)
#        f.SetPointSize(10)
#        f.SetWeight(wx.FONTWEIGHT_NORMAL)
#
#        da = wx.TextAttr(colText=(255, 100, 0))
#        da.SetFont(f)
#
#        ha2 = wx.TextAttr()
#        f.SetPointSize(12)
#        f.SetUnderlined(True)
#        ha2.SetFont(f)
#
#        ba = wx.TextAttr()
#        f.SetUnderlined(False)
#        ba.SetFont(f)
#        f.SetPointSize(10)
#
#        styles = {1:ha1,
#                  2:da,
#                  (3, 4, 5, 6):ba,
#                  7:ha2,
#                  (8, 9, 10, 11):ba
#                  }
#
#        v = View(Item('summary', show_label=False,
##                      editor=HTMLEditor()
#                        style='custom',
#                        editor=SelectableReadonlyTextEditor(
#                        styles=styles,
#                        )
#                      )
#                 )
#        return v
