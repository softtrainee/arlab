#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import List, Str, Bool, Any, Enum, Button
#============= standard library imports ========================
#============= local library imports  ==========================
from src.column_sorter_mixin import ColumnSorterMixin
from src.database.orms.isotope.gen import gen_ProjectTable
from src.experiment.tasks.browser.record_views import ProjectRecordView, SampleRecordView
from src.experiment.tasks.browser.table_configurer import SampleTableConfigurer


DEFAULT_SPEC = 'Spectrometer'
DEFAULT_AT = 'Analysis Type'
DEFAULT_ED = 'Extraction Device'


class BrowserMixin(ColumnSorterMixin):
    projects = List
    oprojects = List

    samples = List  # Property(depends_on='selected_project')
    osamples = List

    project_filter = Str
    sample_filter = Str

    selected_project = Any
    selected_sample = Any

    auto_select_analysis = Bool(True)

    sample_filter_values = List
    sample_filter_parameter = Str('Sample')
    sample_filter_comparator = Enum('=', 'not =')
    sample_filter_parameters = List(['Sample', 'Material'])

    configure_sample_table = Button
    clear_selection_button = Button

    filter_non_run_samples = Bool(True)

    sample_tabular_adapter = Any

    def set_projects(self, ps, sel):
        self.oprojects = ps
        self.projects = ps
        self.trait_set(selected_project=sel)

    def set_samples(self, s, sel):
        self.samples = s
        self.osamples = s
        self.trait_set(selected_sample=sel)

    def activate(self):
        self.load_projects()

    def load_projects(self):
        db = self.manager.db
        with db.session_ctx():
            ps = db.get_projects(order=gen_ProjectTable.name.asc())

            ad = [ProjectRecordView(p) for p in ps]
            self.projects = ad
            self.oprojects = ad

    def _selected_project_changed(self, new):
        if new:
            db = self.manager.db
            with db.session_ctx():
                self._set_samples()
                sams = self.samples
                if sams:
                    self.selected_sample = sams[:1]

                p = self._get_sample_filter_parameter()
                self.sample_filter_values = [getattr(si, p) for si in sams]

    def _filter_non_run_samples_changed(self):
        self._set_samples()

    def _configure_sample_table_fired(self):
        s = SampleTableConfigurer(adapter=self.sample_tabular_adapter,
                                  title='Configure Sample Table',
                                  parent=self
        )
        s.edit_traits()


    def _set_samples(self):
        db = self.manager.db
        with db.session_ctx():
            sams = []
            sp = self.selected_project
            if not hasattr(sp, '__iter__'):
                sp = (sp,)

            for pp in sp:
                ss = db.get_samples(project=pp.name)

                test = lambda x: True
                if self.filter_non_run_samples:
                    def test(sa):
                        return any([len(li.analyses) for li in sa.labnumbers])

                ss = [SampleRecordView(s) for s in ss if test(s)]
                sams.extend(ss)

            self.samples = sams
            self.osamples = sams

    def _filter_func(self, new, attr=None, comp=None):
        comp_keys = {'=': '__eq__',
                     '<': '__lt__',
                     '>': '__gt__',
                     '<=': '__le__',
                     '>=': '__ge__',
                     'not =': '__ne__'
        }
        if comp:
            if comp in comp_keys:
                comp_key = comp_keys[comp]
            else:
                comp_key = comp

        def func(x):
            if attr:
                x = getattr(x, attr.lower())

            if comp is None:
                return x.lower().startswith(new.lower())
            else:
                return getattr(x, comp_key)(new)

        return func

    def _project_filter_changed(self, new):
        self.projects = filter(self._filter_func(new, 'name'), self.oprojects)

    def _sample_filter_changed(self, new):
        name = self._get_sample_filter_parameter()
        #comp=self.sample_filter_comparator
        self.samples = filter(self._filter_func(new, name), self.osamples)

    def _get_sample_filter_parameter(self):
        p = self.sample_filter_parameter
        if p == 'Sample':
            p = 'name'

        return p.lower()

    def _sample_filter_parameter_changed(self, new):
        if new:
            vs = []
            p = self._get_sample_filter_parameter()
            for si in self.osamples:
                v = getattr(si, p)
                if not v in vs:
                    vs.append(v)

            self.sample_filter_values = vs

    def _clear_selection_button_fired(self):
        self.selected_project = []
        self.selected_sample = []


#===============================================================================
# handlers
#===============================================================================

#============= EOF =============================================
