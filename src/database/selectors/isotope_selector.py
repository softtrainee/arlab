#===============================================================================
# Copyright 2011 Jake Ross
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
from traits.api import HasTraits, Any, List, String, \
    Float, Bool, Int, Instance, Property, Dict, Enum, on_trait_change, \
    Str
from traitsui.api import VGroup, HGroup, Item, Group, View, ListStrEditor, \
    InstanceEditor, ListEditor, EnumEditor, Label
#============= standard library imports ========================

#============= local library imports  ==========================
from src.database.selectors.db_selector import DBSelector
from src.graph.time_series_graph import TimeSeriesStackedGraph
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.database.selectors.base_db_result import DBResult
from src.database.orms.isotope_orm import AnalysisTable

from traitsui.wx.text_editor import CustomEditor
import wx
from src.graph.regression_graph import StackedTimeSeriesRegressionGraph

from traitsui.editors.text_editor \
    import ToolkitEditorFactory, evaluate_trait

class _TextEditor(CustomEditor):
    evaluate = evaluate_trait
    parent = Any
    def init(self, parent):
        super(_TextEditor, self).init(parent)
        self.control.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)

        p = 0
        for i, l in enumerate(self.value.split('\n')):
            e = len(l)
            st = next((st for st in self.factory.styles if st == i or
                                                            (i in st if isinstance(st, tuple) else False)

                       ), None)

            if st:
                sa = self.factory.styles[st]
                self.control.SetStyle(p, p + e + 1, sa)
            p += e + 1


    def onKeyDown(self, event):
        if event.CmdDown():
            event.Skip()


class SelectableReadonlyTextEditor(ToolkitEditorFactory):
    tabs = List
    styles = Dict
    def _get_custom_editor_class(self):
        return _TextEditor


class AnalysisSummary(HasTraits):
    age = Float
    error = Float
    result = Any

    summary = Property(depends_on='age,err')

    header1 = ['ID', 'Date', 'Time']
    header2 = ['Detector', 'Signal']

    def _get_summary(self):
        from jinja2 import Template
        doc = '''
{{header1}}
{{data1}}

Name:{{result.filename}}
Root:{{result.directory}}

{{header2}}
{%- for k,v in signals %}
{{k}}\t{{v}} 
{%- endfor %}

Age : {{obj.age}}\xb1{{obj.error}}    
'''

        data1 = map(lambda x: getattr(self.result, x), ['rid', 'rundate', 'runtime'])

        temp = Template(doc)
        join = lambda f, n: ('\t' * n).join(f)
#        join = '\t\t\t'.join
        entab = lambda x:map('{}'.format, map(str, x))
        makerow = lambda x, n: join(entab(x), n)
        result = self.result
        r = temp.render(result=result,
                           header1=makerow(self.header1, 3),
                           header2=makerow(self.header2, 1),
                           data1=makerow(data1, 3),
                           signals=zip(result.iso_keys,
                                       result.intercepts
                                       ),
                           obj=self,
                           )
        return r

    def traits_view(self):
#        s = 51
        ha1 = wx.TextAttr()
        f = wx.Font(12, wx.MODERN, wx.NORMAL,
                         wx.NORMAL, False, u'Consolas')
        f.SetUnderlined(True)
        ha1.SetFont(f)
        ha1.SetTabs([200, ])

        f.SetUnderlined(False)
        f.SetPointSize(10)
        f.SetWeight(wx.FONTWEIGHT_NORMAL)

        da = wx.TextAttr(colText=(255, 100, 0))
        da.SetFont(f)

        ha2 = wx.TextAttr()
        f.SetPointSize(12)
        f.SetUnderlined(True)
        ha2.SetFont(f)

        ba = wx.TextAttr()
        f.SetUnderlined(False)
        ba.SetFont(f)
        f.SetPointSize(10)

        styles = {1:ha1,
                  2:da,
                  (3, 4, 5, 6):ba,
                  7:ha2,
                  (8, 9, 10, 11):ba
                  }

        v = View(Item('summary', show_label=False,
#                      editor=HTMLEditor()
                        style='custom',
                      editor=SelectableReadonlyTextEditor(
                        styles=styles,
                        )
                      )
                 )
        return v

class Analyzer(HasTraits):
    fith2 = Str
    fith1 = Str
    fitax = Str
    fitl1 = Str
    fitl2 = Str
    fitcdd = Str

    filterh2 = Str(enter_set=True, auto_set=False)
    filterh1 = Str(enter_set=True, auto_set=False)
    filterax = Str(enter_set=True, auto_set=False)
    filterl1 = Str(enter_set=True, auto_set=False)
    filterl2 = Str(enter_set=True, auto_set=False)
    filtercdd = Str(enter_set=True, auto_set=False)

    @on_trait_change('fit+,filter+')
    def _changed(self, name, new):

        if new.startswith('fit'):
            attr = 'fit_types'
            trim = 3
        else:
            attr = 'filters'
            trim = 6

        name = name[trim:].upper()
        plotid = list(self.analysis.iso_keys).index(name)
        g = self.analysis.signal_graph
        getattr(g, attr)[plotid] = new

        g._metadata_changed()

    def traits_view(self):
        grp = VGroup()
        keys = list(self.analysis.iso_keys)
        keys.reverse()
        for det in keys:
            g = HGroup(
                       Item('fit{}'.format(det.lower()), label=det.upper(),
                            editor=EnumEditor(values=['linear', 'parabolic',
                                               'cubic'
                                               ])
                            ),
                       Item('filter{}'.format(det.lower()), show_label=False
                            )

                )

            grp.content.append(g)

        v = View(grp)
        return v

class AnalysisResult(DBResult):
    title_str = 'Analysis'
    window_height = 600
    window_width = 650

    sniff_graph = Instance(StackedTimeSeriesRegressionGraph)
    signal_graph = Instance(StackedTimeSeriesRegressionGraph)
    baseline_graph = Instance(StackedTimeSeriesRegressionGraph)
#    sniff_graph = Instance(TimeSeriesStackedGraph)
#    signal_graph = Instance(TimeSeriesStackedGraph)
#    baseline_graph = Instance(TimeSeriesStackedGraph)
    analyzer = Instance(Analyzer)

    categories = List(['summary', 'signal', 'sniff', 'baseline', 'analyzer'])
    selected = Any('signal')
    display_item = Instance(HasTraits)

    iso_keys = None
    intercepts = None

    def traits_view(self):
        info = self._get_info_grp()
        info.label = 'Info'
        grp = HGroup(
                        Item('categories', editor=ListStrEditor(
                                                                editable=False,
                                                                operations=[],
                                                                selected='selected'
                                                                ),
                             show_label=False,
                             width=0.10
                             ),
                        Item('display_item', show_label=False, style='custom'),
                        )

        return self._view_factory(grp)

    def _selected_changed(self):
        if self.selected is not None:

            if self.selected == 'analyzer':
                item = self.analyzer
#                info = self.analyzer.edit_traits()
#                if info.result:
#                    self.analyzer.apply_fits()
            elif self.selected == 'summary':
                item = AnalysisSummary(age=10.0,
                                       error=0.01,
                                       result=self
                                       )
                item.age = 12

            else:
                item = getattr(self, '{}_graph'.format(self.selected))
            self.trait_set(display_item=item)

    def load_graph(self, graph=None, xoffset=0):
        keys, sniffs, signals, baselines = self._get_data()

        self.iso_keys = keys

#        signals = [('a', ([1, 2, 3, 4, 5],
#                  [1, 2, 3, 3.5, 5])
#                  )]

        graph = self._load_graph(signals)

        self.intercepts = [3.3, ] * len(keys)

        self.signal_graph = graph
        self.display_item = graph

        graph = self._load_graph(sniffs)
        self.sniff_graph = graph

        graph = self._load_graph(baselines)
        self.baseline_graph = graph

#        self.selected = 'analyzer'

        self.analyzer = Analyzer(analysis=self)
        self.analyzer.fits = ['linear', ] * len(keys)

    def _load_graph(self, data):
        graph = self._graph_factory(klass=StackedTimeSeriesRegressionGraph)

        gkw = dict(xtitle='Time',
                       padding=[50, 50, 40, 40],
                       panel_height=50,
                       )

        for i, (key, (xs, ys)) in enumerate(data):
            gkw['ytitle'] = key

            graph.new_plot(**gkw)
            graph.new_series(xs, ys, plotid=i)
#            graph.set_series_label(key, plotid=i)

            params = dict(orientation='right' if i % 2 else 'left',
                          axis_line_visible=False
                          )
            graph.set_axis_traits(i, 'y', **params)

        return graph

    def _get_table_data(self, dm, grp):
        return [(ti.name, zip(*[(r['time'], r['value']) for r in ti.iterrows()]))
              for ti in dm.get_tables(grp)]

    def _get_data(self):
        dm = self._data_manager_factory()
        dm.open_data(self._get_path())

        sniffs = []
        signals = []
        baselines = []
        keys = []
        if isinstance(dm, H5DataManager):

            sniffs = self._get_table_data(dm, 'sniffs')
            signals = self._get_table_data(dm, 'signals')
            baselines = self._get_table_data(dm, 'baselines')
            if sniffs or signals or baselines:
                self._loadable = True
                keys = set(zip(*sniffs)[0] if sniffs else [] +
                           zip(*signals)[0] if signals else [] +
                           zip(*baselines)[0] if baselines else []
                           )
        return keys, sniffs, signals, baselines

class IsotopeAnalysisSelector(DBSelector):
    title = 'Recall Analyses'

    parameter = String('AnalysisTable.rundate')
    query_table = AnalysisTable
    result_klass = AnalysisResult
#    multi_graphable = Bool(True)

#    def _load_hook(self):
#        jt = self._join_table_parameters
#        if jt:
#            self.join_table_parameter = str(jt[0])

    def _get_selector_records(self, **kw):
        return self._db.get_analyses(**kw)

#    def _get__join_table_parameters(self):
#        dv = self._db.get_devices()
#        return list(set([di.name for di in dv if di.name is not None]))



#        f = lambda x:[str(col)
#                           for col in x.__table__.columns]
#        params = f(b)
#        return list(params)
#        return

#============= EOF =============================================
