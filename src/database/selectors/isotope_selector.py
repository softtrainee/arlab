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
    Float, Bool, Int, Instance, Property
from traitsui.api import VGroup, HGroup, Item, Group, View, ListStrEditor
#============= standard library imports ========================
from numpy import array
#============= local library imports  ==========================
from src.database.selectors.db_selector import DBSelector
from src.graph.time_series_graph import TimeSeriesStackedGraph
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.database.selectors.base_db_result import DBResult
from src.database.orms.isotope_orm import AnalysisTable

from traitsui.wx.text_editor import CustomEditor
import wx

from traitsui.editors.text_editor \
    import ToolkitEditorFactory, evaluate_trait

class _TextEditor(CustomEditor):
    evaluate = evaluate_trait
    parent = Any
    def init(self, parent):
        super(_TextEditor, self).init(parent)
        self.control.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)

        ta = wx.TextAttr()
        tcFont = wx.Font(10, wx.MODERN, wx.NORMAL,
                         wx.NORMAL, False, u'Consolas')

        he = 1000
        if self.factory.header:
            tcFont.SetWeight(wx.FONTWEIGHT_BOLD)
            tcFont.SetUnderlined(True)
            hs = self.factory.header
            ta.SetFont(tcFont)

            if self.factory.tabs:
                ta.SetTabs(self.factory.tabs)
            self.control.SetStyle(0, hs, ta)

        else:
            hs = 0

        tcFont.SetUnderlined(False)
        tcFont.SetPointSize(10)
        tcFont.SetWeight(wx.FONTWEIGHT_NORMAL)
        ta.SetFont(tcFont)

        self.control.SetStyle(hs, he, ta)

    def onKeyDown(self, event):
        if event.CmdDown():
            event.Skip()


class SelectableReadonlyTextEditor(ToolkitEditorFactory):
    tabs = List
    header = Int
    def _get_custom_editor_class(self):
        return _TextEditor


class AnalysisSummary(HasTraits):
    age = Float
    error = Float
    result = Any
#    summary = String
    summary = Property(depends_on='age,err')

#def _plusminus_sigma(self, n=1):
#        s = unicode('\xb1{}'.format(n)) + unicode('\x73', encoding='Symbol')
#        return s
    header = ['ID', 'Date', 'Time       ']
    def _get_summary(self):
        from jinja2 import Template
        doc = '''
{{header}}
{{data1}}

Name:{{result.filename}}
Root:{{result.directory}}

Age : {{obj.age}}\xb1{{obj.error}}    
'''

        data1 = map(lambda x: getattr(self.result, x), ['rid', 'rundate', 'runtime'])
#        data1 = [1, 2, 3]
        temp = Template(doc)
        join = '\t'.join
        entab = lambda x:map('{}'.format, map(str, x))
        makerow = lambda x: join(entab(x))

        return temp.render(result=self.result,
                           header=makerow(self.header),
                           data1=makerow(data1),
                           obj=self,
                           )


    def traits_view(self):

        v = View(Item('summary', show_label=False,
#                      editor=HTMLEditor()
                        style='custom',
                      editor=SelectableReadonlyTextEditor(
                        tabs=[300, 600],
                        header=len(''.join(self.header)) + 1
                        )
                      )

                 )
        return v

class AnalysisResult(DBResult):
    title_str = 'Analysis'
    window_height = 600
    window_width = 650

    sniff_graph = Instance(TimeSeriesStackedGraph)
    signal_graph = Instance(TimeSeriesStackedGraph)
    baseline_graph = Instance(TimeSeriesStackedGraph)

    categories = List(['summary', 'signal', 'sniff', 'baseline'])
    selected = Any('signal')
    display_item = Instance(HasTraits)

    def traits_view(self):
        info = self._get_info_grp()
        info.label = 'Info'
        grp = HGroup(
                        Item('categories', editor=ListStrEditor(editable=False,
                                                                selected='selected'),
                             show_label=False,
                             width=0.10
                             ),
                        Item('display_item', show_label=False, style='custom'),
                        )

        return self._view_factory(grp)

    def _selected_changed(self):
        if self.selected is not None:
            if self.selected == 'summary':
                item = AnalysisSummary(age=10.0,
                                       error=0.01,
                                       result=self
                                       )
            else:
                item = getattr(self, '{}_graph'.format(self.selected))
            self.trait_set(display_item=item)

    def load_graph(self, graph=None, xoffset=0):
        sniffs, signals, baselines = self._get_data()

        graph = self._load_graph(signals)
        self.signal_graph = graph
        self.display_item = graph

        graph = self._load_graph(sniffs)
        self.sniff_graph = graph

        graph = self._load_graph(baselines)
        self.baseline_graph = graph

        self.selected = 'summary'

    def _load_graph(self, data):
        graph = self._graph_factory(klass=TimeSeriesStackedGraph)

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
        if isinstance(dm, H5DataManager):

            sniffs = self._get_table_data(dm, 'sniffs')
            signals = self._get_table_data(dm, 'signals')
            baselines = self._get_table_data(dm, 'baselines')
            if sniffs or signals or baselines:
                self._loadable = True

        return sniffs, signals, baselines

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
