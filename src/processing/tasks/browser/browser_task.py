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
from datetime import timedelta
from traits.api import List, Str, Bool, Any, Enum, String, \
    Button, on_trait_change, Date, Int, Time, Instance
from pyface.tasks.task_layout import TaskLayout, PaneItem
from pyface.tasks.action.schema import SToolBar
#============= standard library imports ========================
#============= local library imports  ==========================
from src.database.orms.isotope.gen import gen_MassSpectrometerTable, gen_LabTable, gen_ExtractionDeviceTable, \
    gen_AnalysisTypeTable, gen_ProjectTable
from src.database.orms.isotope.meas import meas_MeasurementTable, meas_AnalysisTable, meas_ExtractionTable
from src.envisage.tasks.editor_task import BaseEditorTask
from src.processing.tasks.browser.actions import NewBrowserEditorAction
from src.processing.tasks.browser.analysis_table import AnalysisTable
from src.processing.tasks.browser.panes import BrowserPane
from src.processing.tasks.browser.record_views import ProjectRecordView, SampleRecordView
from src.processing.tasks.recall.recall_editor import RecallEditor
from src.database.records.isotope_record import IsotopeRecordView

'''
add toolbar action to open another editor tab


'''

"""
@todo: how to fit cocktail/air blanks. make special project called references.
added sample to air, cocktail. added samples to references project
"""

DEFAULT_SPEC = 'Spectrometer'
DEFAULT_AT = 'Analysis Type'
DEFAULT_ED = 'Extraction Device'


class BaseBrowserTask(BaseEditorTask):
    projects = List
    oprojects = List

    samples = List  # Property(depends_on='selected_project')
    osamples = List

    #analyses = List
    #oanalyses = List

    analysis_table = Instance(AnalysisTable, ())
    danalysis_table = Instance(AnalysisTable, ())

    project_filter = Str
    sample_filter = Str
    analysis_filter = String(enter_set=True, auto_set=False)

    selected_project = Any
    selected_sample = Any

    dclicked_sample = Any

    tool_bars = [SToolBar(NewBrowserEditorAction(),
                          image_size=(16, 16))]

    auto_select_analysis = Bool(True)

    sample_filter_values = List
    sample_filter_parameter = Str('Sample')
    sample_filter_comparator = Enum('=', 'not =')
    sample_filter_parameters = List(['Sample', 'Material'])

    mass_spectrometer = Str(DEFAULT_SPEC)
    mass_spectrometers = List
    analysis_type = Str(DEFAULT_AT)
    analysis_types = List
    extraction_device = Str(DEFAULT_ED)
    extraction_devices = List
    start_date = Date
    start_time = Time

    end_date = Date
    end_time = Time
    days_pad = Int(0)
    hours_pad = Int(18)

    clear_selection_button = Button

    default_reference_analysis_type = 'blank_unknown'
    auto_select_references = Bool(False)

    filter_non_run_samples = Bool(True)

    def activated(self):
        self.load_projects()

        db = self.manager.db
        with db.session_ctx():
            self._load_mass_spectrometers()
            self._load_analysis_types()
            self._load_extraction_devices()
        self._set_db()

    def _set_db(self):
        self.analysis_table.db = self.manager.db
        self.danalysis_table.db = self.manager.db

    def _load_mass_spectrometers(self):
        db = self.manager.db
        ms = [mi.name for mi in db.get_mass_spectrometers()]
        self.mass_spectrometers = ['Spectrometer', 'None'] + ms

    def _load_analysis_types(self):
        db = self.manager.db
        ms = [mi.name for mi in db.get_analysis_types()]
        self.analysis_types = ['Analysis Type', 'None'] + ms

    def _load_extraction_devices(self):
        db = self.manager.db
        ms = [mi.name for mi in db.get_extraction_devices()]
        self.extraction_devices = ['Extraction Device', 'None'] + ms

    def load_projects(self):
        db = self.manager.db
        with db.session_ctx():
            ps = db.get_projects(order=gen_ProjectTable.name.asc())

            ad = [ProjectRecordView(p) for p in ps]
            self.projects = ad
            self.oprojects = ad
        db = self.manager.db

    def _create_browser_pane(self, **kw):
        return BrowserPane(model=self, **kw)

    def _selected_project_changed(self, new):
        if new:
            db = self.manager.db
            with db.session_ctx():
                self._set_samples()
                sams = self.samples
                if sams:
                    #print sams[:1]
                    self.selected_sample = sams[:1]

                p = self._get_sample_filter_parameter()
                self.sample_filter_values = [getattr(si, p) for si in sams]

    def _filter_non_run_samples_changed(self):
        self._set_samples()

    def _set_samples(self):
        db = self.manager.db
        with db.session_ctx():
            sams = []
            for pp in self.selected_project:
                ss = db.get_samples(project=pp.name)

                test = lambda x: True
                if self.filter_non_run_samples:
                    def test(sa):
                        return any([len(li.analyses) for li in sa.labnumbers])

                ss = [SampleRecordView(s) for s in ss if test(s)]
                sams.extend(ss)

            self.samples = sams
            self.osamples = sams

    def _get_sample_analyses(self, srv, limit=50):
        db = self.manager.db
        with db.session_ctx():
            for project in self.selected_project:
                sample = db.get_sample(srv.name,
                                       project=project.name)
                if sample:
                    break
            else:
                return []

            ans = db.get_sample_analyses(sample, limit=limit)
            return [self._record_view_factory(a) for a in ans]

    def _record_view_factory(self, ai):
        iso = IsotopeRecordView()
        iso.create(ai)
        return iso

    def _selected_sample_changed(self, new):
        if new:
            ans = []
            for ni in new:
                aa = self._get_sample_analyses(ni)
                #print 'aa', new, ans
                ans.extend(aa)

            ans = self.analysis_table.set_analyses(ans)

            if ans and self.auto_select_analysis:
                self.analysis_table.selected_analysis = ans[0]

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
        self.analysis_table.selected_analysis = []

    def _ok_query(self):
        ms = self.mass_spectrometer not in (DEFAULT_SPEC, 'None')
        at = self.analysis_type not in (DEFAULT_AT, 'None')

        return ms and at

    def _ok_ed(self):
        return self.extraction_device not in (DEFAULT_ED, 'None')

    @on_trait_change('mass_spectrometer, analysis_type, extraction_device')
    def _query(self):
        if self._ok_query():

            db = self.manager.db
            with db.session_ctx() as sess:
                q = sess.query(meas_AnalysisTable)
                q = q.join(gen_LabTable)
                q = q.join(meas_MeasurementTable)
                q = q.join(gen_MassSpectrometerTable)
                q = q.join(gen_AnalysisTypeTable)

                if self._ok_ed():
                    q = q.join(meas_ExtractionTable)
                    q = q.join(gen_ExtractionDeviceTable)

                name = self.mass_spectrometer
                q = q.filter(gen_MassSpectrometerTable.name == name)
                if self._ok_ed():
                    q = q.filter(gen_ExtractionDeviceTable.name == self.extraction_device)

                q = q.filter(gen_AnalysisTypeTable.name == self.analysis_type)
                q = q.order_by(meas_AnalysisTable.analysis_timestamp.desc())
                q = q.limit(200)

                ans = q.all()

                aa = [self._record_view_factory(ai) for ai in ans]

                self.danalysis_table.analyses = aa
                self.danalysis_table.oanalyses = aa
        else:
            if self.mass_spectrometer == 'None':
                self.mass_spectrometer = DEFAULT_SPEC
            if self.extraction_device == 'None':
                self.extraction_device = DEFAULT_ED
            if self.analysis_type == 'None':
                self.analysis_type = DEFAULT_AT

    @on_trait_change('analysis_table:selected_analysis')
    def _selected_analysis_changed(self, new):
        self._set_selected_analysis(new)

    def _set_selected_analysis(self, new):
        if not new:
            return

        if not self.auto_select_references:
            return

        if not hasattr(new, '__iter__'):
            new = (new, )

        ds = [ai.timestamp for ai in new]
        dt = timedelta(days=self.days_pad, hours=self.hours_pad)

        sd = min(ds) - dt
        ed = max(ds) + dt

        self.start_date = sd.date()
        self.end_date = ed.date()
        self.start_time = sd.time()
        self.end_time = ed.time()

        at = self.analysis_type

        if self.analysis_type == DEFAULT_AT:
            self.analysis_type = at = self.default_reference_analysis_type

        ref = new[-1]
        exd = ref.extract_device
        ms = ref.mass_spectrometer
        self.extraction_device = exd or 'Extraction Device'
        self.mass_spectrometer = ms or 'Mass Spectrometer'

        db = self.manager.db
        with db.session_ctx():
            ans = db.get_analyses_data_range(sd, ed,
                                             analysis_type=at,
                                             mass_spectrometer=ms,
                                             extract_device=exd
            )
            ans = [self._record_view_factory(ai) for ai in ans]
            self.danalysis_table.set_analyses(ans)

    def _dclicked_sample_changed(self):
        ans = self._get_sample_analyses(self.selected_sample[-1])
        #print self.active_editor
        if self.active_editor:
            self.active_editor.unknowns = ans
            self.unknowns_pane.items = self.active_editor.unknowns


class BrowserTask(BaseBrowserTask):
    name = 'Analysis Browser'


    def activated(self):
        editor = RecallEditor()
        self._open_editor(editor)
        self.load_projects()

    def new_editor(self):
        editor = RecallEditor()
        self._open_editor(editor)

    def _default_layout_default(self):
        return TaskLayout(left=PaneItem('pychron.browser'))

    def _set_selected_analysis(self, an):
        if an and isinstance(self.active_editor, RecallEditor):
        #             l, a, s = strip_runid(s)
        #             an = self.manager.db.get_unique_analysis(l, a, s)
            an = self.manager.make_analyses([an])[0]
            #             an.load_isotopes(refit=False)
            #self.active_editor.analysis_summary = an.analysis_summary
            self.active_editor.analysis_view = an.analysis_view

    def create_dock_panes(self):
        return [self._create_browser_pane(multi_select=False)]

    def _analysis_table_default(self):
        at = AnalysisTable(db=self.manager.db)
        return at

    def _danalysis_table_default(self):
        at = AnalysisTable(db=self.manager.db)
        return at

    def _dclicked_sample_changed(self):
        pass

#===============================================================================
# handlers
#===============================================================================

#============= EOF =============================================
