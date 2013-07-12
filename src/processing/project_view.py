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
from traits.api import HasTraits, Instance, cached_property, Property, Any, \
    List, Bool, Event, Button, DelegatesTo
from traitsui.api import View, Item, HGroup, spring, VGroup, \
    EnumEditor, TabularEditor
from traitsui.tabular_adapter import TabularAdapter
#============= standard library imports ========================

#============= local library imports  ==========================
from src.processing.analysis import Analysis
from src.database.records.isotope_record import IsotopeRecord
from src.processing.tabular_analysis_manager import AnalysisAdapter
from src.viewable import Viewable
from src.processing.plotter_options_manager import IdeogramOptionsManager

# class Panel(HasTraits):
#    pass

class SamplesAdapter(TabularAdapter):
    columns = [('Name', 'name')]

class Sample(HasTraits):
    name = Property
    dbrecord = Any
    analyses = Property
    def _get_name(self):
        return self.dbrecord.name

    @cached_property
    def _get_analyses(self):
        ans = [Analysis(isotope_record=IsotopeRecord(_dbrecord=ri))
                    for ln in self.dbrecord.labnumbers
                        for ri in ln.analyses]

        return ans

class ProjectView(Viewable):
#    lpanel = Instance(Panel)
#    rpanel = Instance(Panel)
    plotter_options_manager = Instance(IdeogramOptionsManager, ())
    plotter_options = DelegatesTo('plotter_options_manager')
    plotter_options_list = DelegatesTo('plotter_options_manager')

    project = Any
    projects = Property

    samples = Property(List(Sample), depends_on='project')
    selected_sample = Any
    update_selected_sample = Event

    analyses = Property(List(Analysis), depends_on='selected_sample, project')
    selected_analysis = Any
    update_selected_analysis = Event

    only_fusions = Bool(True)
    include_omitted = Bool(True)
    highlight_omitted = Bool(True)

    edit_plotter_options = Button('Edit')
    def get_filtered_analyses(self):
        sam = self.selected_sample
        if sam:
            ans = sam.analyses
            if self.only_fusions:
                ans = filter(lambda x: x.step == '', ans)
            if not self.include_omitted:
                ans = filter(lambda x: x.status == 0, ans)
            return ans

#===============================================================================
# persistence
#===============================================================================

#===============================================================================
# handlers
#===============================================================================

    def _update_selected_analysis_fired(self):
        sa = self.selected_analysis
        if sa is not None:
            dbr = sa.isotope_record
            dbr.load_graph()
            dbr.edit_traits()

    def _edit_plotter_options_fired(self):
        po = self.plotter_options_manager
        info = po.edit_traits(kind='livemodal')
        if info.result:
            po.set_plotter_options(self.plotter_options.name)

#===============================================================================
# property get/set
#===============================================================================
    @cached_property
    def _get_projects(self):
        prs = dict([(pi, pi.name) for pi in self.db.get_projects()])
        if prs:
            self.project = pi
        return prs

    @cached_property
    def _get_samples(self):
        ss = []
        pr = self.project
        if pr:
            ss = [Sample(dbrecord=si
                           ) for si in pr.samples]
        return ss

    @cached_property
    def _get_analyses(self):
        ans = []
        if self.selected_sample:
            ans = self.selected_sample.analyses
        return ans

#    @cached_property
#    def _get_plotter_options_list(self):
#        r = paths.plotter_options_dir
#        ps = [IdeogramOptions(name=NULL_STR)]
#        for n in os.listdir(r):
#            if n.startswith('.'):
#                continue
#            if n.endswith('.default'):
#                continue
#
#            po = IdeogramOptions(name=n)
#            ps.append(po)
#
#        return ps
#
#    def _plotter_options_default(self):
#        p = os.path.join(paths.plotter_options_dir, 'project_view.default')
#        if os.path.isfile(p):
#            with open(p, 'r') as fp:
#                try:
#                    n = pickle.load(fp)
#                except pickle.PickleError:
#                    n = NULL_STR
#
#            return next((pi for pi in self.plotter_options_list if pi.name == n), None)

#        return self._load_plotter_options()

    def traits_view(self):
#        l = Item('lpanel', style='custom', show_label=False, width=0.25)
#        r = Item('rpanel', style='custom', show_label=False, width=0.75)
#
#        v = View(HGroup(l, r))
        prj = Item('project', show_label=False,
                   editor=EnumEditor(name='projects'))
        samples = Item('samples', show_label=False,
                       editor=TabularEditor(adapter=SamplesAdapter(),
                                            selected='selected_sample',
                                            dclicked='update_selected_sample',
                                            editable=False
                                            ))


        analyses = Item('analyses', show_label=False,
                      editor=TabularEditor(adapter=AnalysisAdapter(),
                                           selected='selected_analysis',
                                           dclicked='update_selected_analysis',
                                           editable=False
                                           )
                      )
        options_grp = VGroup(
                           Item('only_fusions', label='Display Only Fusion Analyses'),
                           Item('include_omitted', label='Include Omitted Analyses'),
                           Item('highlight_omitted', label='Highlight Omitted Analyses',
                                enabled_when='include_omitted')
                           )

        graph_options = HGroup(Item('plotter_options', show_label=False,
                                   editor=EnumEditor(name='plotter_options_list')
                                ),
                               Item('edit_plotter_options', show_label=False)
                              )

        grp = VGroup(HGroup(prj, spring, options_grp),
                     graph_options,
                     samples,
                     analyses
                     )
        v = View(grp,
                 width=500,
                 height=500,
                 handler=self.handler_klass,
                 resizable=True
                 )
        return v

if __name__ == '__main__':
    from launchers.helpers import build_version
    from src.paths import paths
    build_version('_experiment')
    from src.paths import build_directories
    build_directories(paths)
    from src.globals import globalv
    globalv.show_infos = False
    globalv.show_warnings = False

    from src.helpers.logger_setup import logging_setup
    logging_setup('processing')
    pv = ProjectView()
    pv.db.connect()
    pv.configure_traits()
#============= EOF =============================================
#    def _parallel_age_calc(self, ans):
#        import time
#        import wx
#        from Queue import Queue
#
#        n = len(ans)
#        pd = myProgressDialog(max=n, size=(550, 15))
#        def open_progress():
#            pd.open()
#            (w, h) = wx.DisplaySize()
#            (ww, _hh) = pd.control.GetSize()
#            pd.control.MoveXY(w / 2 - ww + 275, h / 2 + 150)
#
#        do_later(open_progress)
# #        time.sleep(0.1)
#        ranalyses = []
#        def add_analysis(q):
#            while 1:
#                a = q.get()
#                if a:
#                    do_after(1, pd.increment)
#                    ranalyses.append(a)
#                    time.sleep(0.0001)
#                else:
#                    break
#
#        q = Queue()
#        adder = Thread(target=add_analysis, args=(q,))
#        adder.start()
#        st = time.time()
#        t = ThreadPool(1)
#        for ai in ans:
#            attr = dict(dbrecord=ai.dbrecord)
#            t.add_task(self._load_analysis, q, ai.uuid, **attr)
#
#        do_later(pd.change_message, 'Finishing calculations')
#        t.wait_completion()
#
#        #send stop signal to adder thread
#        q.put(None)
#        do_later(pd.close)
# #        print time.time() - st
#        return ranalyses
#
#    def _load_analysis(self, queue, n, dbrecord=None, **kw):
#        from src.database.orms.isotope_orm import meas_AnalysisTable
#        sess = self.db.new_session()
#        q = sess.query(meas_AnalysisTable)
#        q = q.filter(meas_AnalysisTable.id == dbrecord._dbrecord.id)
#        dbr = q.one()
# #        print id(dbr), dbr
#        dbrecord._dbrecord = dbr
#        a = Analysis(uuid=n,
#                     dbrecord=dbrecord,
#                         **kw)
#
#        if a.load_age():
#            queue.put(a)
# #            self._analyses.append(a)
# #        sess.expunge_all()
#        sess.close()
#        sess.remove()
