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
from traits.api import HasTraits, List, Instance, Button, Any, Enum, on_trait_change
from traitsui.api import View, Item, Controller, UItem, spring, HGroup, \
    VGroup
from traitsui.tabular_adapter import TabularAdapter
#============= standard library imports ========================
import csv
import os
from uncertainties import ufloat
#============= local library imports  ==========================
from src.loggable import Loggable
from src.traits_editors.tabular_editor import myTabularEditor
from src.experiment.utilities.identifier import make_runid
from src.processing.publisher.writers.pdf_writer import PDFWriter
from src.processing.publisher.writers.csv_writer import CSVWriter
from src.processing.publisher.writers.mass_spec_writer import MassSpecCSVWriter
from src.processing.autoupdate_parser import AutoupdateParser

class LoadedTableAdapter(TabularAdapter):
    columns = [('RunID', 'runid')]

class SelectedTableAdapter(TabularAdapter):
    columns = [('RunID', 'runid')]

class LoadedTable(HasTraits):
    analyses = List
    def load(self, p):
        ap = AutoupdateParser()
        if os.path.isfile(p):
            samples = ap.parse(p, self._analysis_factory)
            self.analyses = samples[0].analyses
#            self.analyses = ans


#            with open(p, 'r') as fp:
#                delim = '\t'
#                reader = csv.reader(fp, delimiter=delim)
#                factory = self._analysis_factory
#                ans = [factory(line) for line in reader]
#                self.analyses = [ai for ai in ans if ai is not None]

    def _analysis_factory(self, params):
        a = PubAnalysis()
        a.set_runid(params['run_id'])
        for si in ('Ar40', 'Ar39', 'Ar38', 'Ar37', 'Ar36'):
            v = params[si]
            e = params['{}Er'.format(si)]
#            print v, e
            setattr(a, si, ufloat(v, e))


        return a

class LoadedTableController(Controller):
    load_button = Button
    selected = Any
#    def controller_selected_changed(self, info):
#        print self.selected

    def controller_load_button_changed(self, info):
        p = '/Users/ross/Sandbox/autoupdate.txt'
        self.model.load(p)

    def traits_view(self):
        v = View(
                 HGroup(spring, UItem('controller.load_button')),
                 UItem('analyses', editor=myTabularEditor(
                                                          multi_select=True,
                                                          selected='controller.selected',
                                                          adapter=LoadedTableAdapter())),

                 )

        return v

class SelectedTable(HasTraits):
    analyses = List

class SelectedTableController(Controller):
    make_button = Button('make')
    style = Enum('Publication', 'Data Repository')
    def controller_make_button_changed(self, info):
#        print info
        # get an output path
        out = '/Users/ross/Sandbox/autoupdate_table.pdf'
        writer = self._new_writer(out)
        ans = self.model.analyses
        writer.add_ideogram_table(ans, add_title=True, add_header=True)
        writer.publish()
        import webbrowser
        webbrowser.open('file://{}'.format(out))
#        for ai in self.model.analyses:
#            print ai

    def _new_writer(self, out, kind='pdf'):
        if kind == 'pdf':
            klass = PDFWriter
        elif kind == 'csv':
            klass = CSVWriter
        elif kind == 'massspec':
            klass = MassSpecCSVWriter
        pub = klass(filename=out)
        return pub

    def traits_view(self):
        v = View(
                 HGroup(spring, UItem('controller.style'),
                        UItem('controller.make_button',
                              enabled_when='analyses'
                              )),
                 UItem('analyses',
                       editor=myTabularEditor(adapter=SelectedTableAdapter(),
                                              ))
                 )
        return v

class Publisher(Loggable):
    loaded_table = Instance(LoadedTableController)
    selected_table = Instance(SelectedTableController)
    append_button = Button('Append')
    replace_button = Button('Replace')

    @on_trait_change('loaded_table:model:analyses[]')
    def _analyses_handler(self, new):
        self.selected_table.model.analyses = new

    def _append_button_fired(self):
        if self.loaded_table.selected:
            self.selected_table.model.analyses.extend(self.loaded_table.selected)

    def _replace_button_fired(self):
        if self.loaded_table.selected:
            self.selected_table.model.analyses = self.loaded_table.selected

    def _loaded_table_default(self):
        return LoadedTableController(LoadedTable())

    def _selected_table_default(self):
        return SelectedTableController(SelectedTable())

    def traits_view(self):
        v = View(
                 HGroup(UItem('loaded_table', style='custom'),
                        VGroup(spring,
                               UItem('append_button'),
                               UItem('replace_button'),
                               spring
                               ),
                        UItem('selected_table', style='custom')),
                 resizable=True,
                 height=300,
                 width=500,
                 x=100,
                 y=100
                 )
        return v

def make_ufloat(*args):
    if not args:
        args = (1, 0)
    return ufloat(*args)

def uone():
    return make_ufloat()


import re
STEP_REGEX = re.compile('\d{2,}\w+')

class PubAnalysis(HasTraits):
    labnumber = 'A'
    aliquot = 0
    step = ''
    sample = 'FC-2'
    material = 'sanidine'
    status = 0


    j = ufloat(1e-4, 1e-7)
    ic_factor = ufloat(1.03, 1e-10)
    rad40 = ufloat(99.0, 0.1)

    k39 = uone()
    moles_Ar40 = uone()

    Ar40 = uone()
    Ar39 = uone()
    Ar38 = uone()
    Ar37 = uone()
    Ar36 = uone()

    Ar40_blank = uone()
    Ar39_blank = uone()
    Ar38_blank = uone()
    Ar37_blank = uone()
    Ar36_blank = uone()

    extract_value = 10

    rad40_percent = uone()

    age = uone()
    blank_fit = 'LR'
    def set_runid(self, rid):
        ln, a = rid.split('-')
        self.labnumber = ln
        if STEP_REGEX.match(a):
            self.step = a[-1]
            self.aliquot = int(a[:-1])
        else:
            self.aliquot = int(a)

    @property
    def runid(self):
        return make_runid(self.labnumber, self.aliquot, self.step)
    @property
    def R(self):
        return self.rad40 / self.k39

if __name__ == '__main__':
    out = '/Users/ross/Sandbox/publish.pdf'

    pub = Publisher()
    pub.configure_traits()
#    pi = pub.writer(out, kind='pdf')

#    ans = [DummyAnalysis(labnumber='4000',
#                         aliquot=i)
#                         for i in range(5)]
#    ta = pi.add_ideogram_table(ans, add_title=True, add_header=True)
#    ans = [DummyAnalysis(labnumber='5000',
#                         aliquot=i
#                         ) for i in range(5)]
#
#    pi.add_ideogram_table(ans,
#                          widths=ta.get_widths(),
#                          add_header=True)
# #    ans = [DummyAnalysis(record_id='6000-{:02n}'.format(i)) for i in range(5)]
# #    pi.add_ideogram_table(ans)
# #    ans = [DummyAnalysis(record_id='7000-{:02n}'.format(i)) for i in range(5)]
# #    pi.add_ideogram_table(ans)
#    pi.publish()
#
#    import webbrowser
#    webbrowser.open('file://{}'.format(out))



#============= EOF =============================================
