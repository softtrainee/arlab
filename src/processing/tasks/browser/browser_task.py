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
from traits.api import HasTraits, List, Str, Bool, Any, Enum, String, \
    Button, on_trait_change, Date
from traitsui.api import View, Item
from pyface.tasks.task_layout import TaskLayout, PaneItem
from pyface.tasks.action.schema import SToolBar
from pyface.tasks.action.task_action import TaskAction
from pyface.image_resource import ImageResource
#============= standard library imports ========================
#============= local library imports  ==========================
from src.database.orms.isotope.gen import gen_MassSpectrometerTable, gen_LabTable, gen_ExtractionDeviceTable, gen_AnalysisTypeTable
from src.database.orms.isotope.meas import meas_MeasurementTable, meas_AnalysisTable, meas_ExtractionTable
from src.envisage.tasks.editor_task import BaseEditorTask
from src.processing.tasks.browser.panes import BrowserPane
from src.processing.tasks.recall.recall_editor import RecallEditor
from src.paths import paths
# from src.database.orms.isotope.gen import gen_SampleTable, gen_ProjectTable
# from src.database.orms.isotope_orm import gen_SampleTable, gen_ProjectTable
# from sqlalchemy.orm import subqueryload
from src.database.records.isotope_record import IsotopeRecordView
from src.processing.analyses.analysis import DBAnalysis
'''
add toolbar action to open another editor tab


'''
class NewBrowserEditorAction(TaskAction):
    method = 'new_editor'
    image = ImageResource(name='add.png',
                         search_path=paths.icon_search_path
                         )

class RecordView(HasTraits):
    def __init__(self, dbrecord):
        self._create(dbrecord)
    def _create(self, *args, **kw):
        pass

class SampleRecordView(RecordView):
    name = Str
    material = Str

    def _create(self, dbrecord):
        self.name = dbrecord.name
        if dbrecord.material:
            self.material = dbrecord.material.name

class ProjectRecordView(RecordView):
    name = Str
    def _create(self, dbrecord):
        self.name = dbrecord.name

class BaseBrowserTask(BaseEditorTask):
    projects = List
    oprojects = List

    samples = List  # Property(depends_on='selected_project')
    osamples = List

    analyses = List  # Property(depends_on='selected_sample')
    oanalyses = List

    project_filter = Str
    sample_filter = Str#(enter_set=True, auto_set=False)
    analysis_filter = String(enter_set=True, auto_set=False)

    selected_project = Any
    selected_sample = Any
    selected_analysis = Any
    dclicked_sample = Any

    omit_invalid = Bool(True)

    tool_bars = [SToolBar(NewBrowserEditorAction(),
                          image_size=(16, 16)
    )]

    auto_select_analysis = Bool(True)

    sample_filter_values = List
    sample_filter_parameter = Str('Sample')
    sample_filter_comparator = Enum('=', 'not =')
    sample_filter_parameters = List(['Sample', 'Material'])

    analysis_filter_values = List
    analysis_filter_comparator = Enum('=', '<', '>', '>=', '<=', 'not =', 'startswith')
    analysis_filter_parameter = Str('Record_id')
    analysis_filter_parameters = List(['Record_id', 'Tag',
                                       'Age', 'Labnumber', 'Aliquot', 'Step'])

    mass_spectrometer = Str
    mass_spectrometers = List
    analysis_type = Str
    analysis_types = List
    extraction_device = Str
    extraction_devices = List
    start_date = Date
    end_date = Date

    configure_analysis_filter = Button
    clear_selection_button = Button

    def activated(self):
        self.load_projects()

        db = self.manager.db
        with db.session_ctx():
            self._load_mass_spectrometers()
            self._load_analysis_types()
            self._load_extraction_devices()

    def _load_mass_spectrometers(self):
        db = self.manager.db
        ms = [mi.name for mi in db.get_mass_spectrometers()]
        self.mass_spectrometers = ms

    def _load_analysis_types(self):
        db = self.manager.db
        ms = [mi.name for mi in db.get_analysis_types()]
        self.analysis_types = ms

    def _load_extraction_devices(self):
        db = self.manager.db
        ms = [mi.name for mi in db.get_extraction_devices()]
        self.extraction_devices = ms

    def load_projects(self):
        db = self.manager.db
        with db.session_ctx():
            ps = db.get_projects()

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
                sams = []
                for pp in new:
                    ss = db.get_samples(project=pp.name)
                    ss = [SampleRecordView(s) for s in ss]
                    sams.extend(ss)

                self.samples = sams
                self.osamples = sams

                if sams:
                    #print sams[:1]
                    self.selected_sample = sams[:1]

                p = self._get_sample_filter_parameter()
                self.sample_filter_values = [getattr(si, p) for si in sams]

    def _get_sample_analyses(self, srv):
        db = self.manager.db
        with db.session_ctx():
            for project in self.selected_project:
                sample = db.get_sample(srv.name,
                                       project=project.name)
                if sample:
                    break
            else:
                return []

            return [self._record_view_factory(a) for ln in sample.labnumbers
                    for a in ln.analyses]

    def _record_view_factory(self, ai):
        print ai
        #iso = IsotopeRecordView()
        #print ai, iso
        #iso.create(ai)
        #return iso
        return 'asf'

    def _selected_sample_changed(self, new):
        if new:
            ans = []
            for ni in new:
                aa = self._get_sample_analyses(ni)
                #print 'aa', new, ans
                ans.extend(aa)

            self.oanalyses = ans

            if self.omit_invalid:
                ans = filter(self._omit_invalid_filter, ans)

            self.analyses = ans
            if ans and self.auto_select_analysis:
                self.selected_analysis = ans[0]

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

    def _omit_invalid_filter(self, x):
        return x.tag != 'invalid'

    def _project_filter_changed(self, new):
        self.projects = filter(self._filter_func(new, 'name'), self.oprojects)

    def _sample_filter_changed(self, new):
        name = self._get_sample_filter_parameter()
        #comp=self.sample_filter_comparator
        self.samples = filter(self._filter_func(new, name), self.osamples)

    def _analysis_filter_changed(self, new):
        if new:
            name = self.analysis_filter_parameter
            comp = self.analysis_filter_comparator
            if name == 'Step':
                new = new.upper()

            self.analyses = filter(self._filter_func(new, name, comp), self.oanalyses)
        else:
            self.analyses = self.oanalyses

    def _omit_invalid_changed(self, new):
        if new:
            self.analyses = filter(self._omit_invalid_filter, self.oanalyses)
        else:
            self.analyses = self.oanalyses

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

    def _get_analysis_filter_parameter(self):
        p = self.analysis_filter_parameter
        return p.lower()

    def _analysis_filter_comparator_changed(self):
        self._analysis_filter_changed(self.analysis_filter)

    def _analysis_filter_parameter_changed(self, new):
        if new:
            vs = []
            p = self._get_analysis_filter_parameter()
            for si in self.oanalyses:
                v = getattr(si, p)
                if not v in vs:
                    vs.append(v)

            self.analysis_filter_values = vs

    def _clear_selection_button_fired(self):
        self.selected_project = []
        self.selected_sample = []
        self.selected_analysis = []

    def _configure_analysis_filter_fired(self):
        print 'fooo'


    @on_trait_change('mass_spectrometer, anaylsis_type, extraction_device')
    def _query(self):
        if self.mass_spectrometer and self.analysis_type:
            db = self.manager.db
            with db.session_ctx() as sess:
                q = sess.query(meas_AnalysisTable)
                q = q.join(gen_LabTable)
                q = q.join(meas_MeasurementTable)
                q = q.join(gen_MassSpectrometerTable)
                q = q.join(gen_AnalysisTypeTable)

                if self.extraction_device:
                    q = q.join(meas_ExtractionTable)
                    q = q.join(gen_ExtractionDeviceTable)

                name = self.mass_spectrometer
                q = q.filter(gen_MassSpectrometerTable.name == name)
                if self.extraction_device:
                    q = q.filter(gen_ExtractionDeviceTable.name == self.extraction_device)

                q = q.filter(gen_AnalysisTypeTable.name == self.analysis_type)
                q = q.order_by(meas_AnalysisTable.analysis_timestamp.desc())
                ans = q.all()

                aa = [self._record_view_factory(ai) for ai in ans]

                self.analyses = aa
                self.oanalyses = aa

    def _extraction_device_changed(self):
        pass


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

    def _selected_analysis_changed(self):
        an = self.selected_analysis
        if an and isinstance(self.active_editor, RecallEditor):
#             l, a, s = strip_runid(s)
#             an = self.manager.db.get_unique_analysis(l, a, s)
            an = self.manager.make_analyses([an])[0]
#             an.load_isotopes(refit=False)
            self.active_editor.analysis_summary = an.analysis_summary

    def create_dock_panes(self):
        return [self._create_browser_pane(multi_select=False)]

#===============================================================================
# handlers
#===============================================================================

#============= EOF =============================================
