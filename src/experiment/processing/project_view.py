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
from launchers.helpers import build_version
build_version('_experiment')
from src.database.records.isotope_record import IsotopeRecord


#============= enthought library imports =======================
from traits.api import HasTraits, Instance, cached_property, Property, Any, Str, \
    List, Bool, Int, Event
from traitsui.api import View, Item, TableEditor, HGroup, spring, VGroup, \
    EnumEditor, TabularEditor
#============= standard library imports ========================
#============= local library imports  ==========================
from src.experiment.processing.database_manager import DatabaseManager
from traitsui.tabular_adapter import TabularAdapter
from src.experiment.processing.script import ProcessScript
from threading import Thread
from pyface.timer.do_later import do_later, do_after
from src.initializer import MProgressDialog
from src.helpers.thread_pool import ThreadPool
from src.experiment.processing.analysis import Analysis, AnalysisTabularAdapter

#class Panel(HasTraits):
#    pass

class SamplesAdapter(TabularAdapter):
    columns = [('Name', 'name')]

class Sample(HasTraits):
    name = Property
    dbrecord = Any
    def _get_name(self):
        return self.dbrecord.name

class AnalysisAdapter(TabularAdapter):
    columns = [('Status', 'status_string'), ('ID', 'record_id'),
               ('Age', 'age'),
               (u'\u00b11s', 'age_error')
#               (unicode('03c3', encoding='symbol'), 'error')
               ]
    status_string_width = Int(40)
    age_text = Property
    age_error_format = Str('%0.4f')
    age_width = Int(80)
    age_error_width = Int(80)

    def _get_age_text(self, trait, item):
        return '{:0.4f}'.format(self.item.age[0])

    def get_font(self, obj, trait, row):
        import wx
        s = 9
        f = wx.FONTFAMILY_DEFAULT
        st = wx.FONTSTYLE_NORMAL
        w = wx.FONTWEIGHT_NORMAL
        return wx.Font(s, f, st, w)

class ProjectView(DatabaseManager):
#    lpanel = Instance(Panel)
#    rpanel = Instance(Panel)
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
    display_omitted = Bool(True)
#    def _lpanel_default(self):
#        p = Panel()
#        return p
#
#    def _rpanel_default(self):
#        p = Panel()
#        return p

    def load_sample_ideogram(self):
        '''
            input a dbsample and plot an ideogram of all analyses
        '''
        ans = self.analyses

#        if self.only_fusions:
#            ans = filter(lambda x: x.step == '', ans)

        if not self.include_omitted:
            ans = filter(lambda x: x.status == 0, ans)

        self._load(ans)
#        t = Thread(target=self._load, args=(ans,))
#        t.start()

    def _load(self, ans):
        ps = ProcessScript()
#        ans = ps._convert_records(recs)
        ps._group_by_labnumber(ans)

        progress = self._open_progress(len(ans))
        for ai in ans:
            msg = 'loading {}'.format(ai.record_id)
            progress.change_message(msg)
            ai.load_age()
            progress.increment()

        rr = ps._ideogram(ans, aux_plots=['analysis_number'], show=False)
        if rr is not None:
            g, ideo = rr
            if self.display_omitted:
                #sort ans by age
                ta = sorted(ans, key=lambda x:x.age)
                #find omitted ans
                sel = [i for i, ai in enumerate(ta) if ai.status != 0]
                ideo.set_excluded_points(sel, 0)

            g.edit_traits()
#        do_later(g.edit_traits)
    def _open_progress(self, n):
        import wx
        pd = MProgressDialog(max=n, size=(550, 15))
        pd.open()

        (w, h) = wx.DisplaySize()
        (ww, _hh) = pd.control.GetSize()
        pd.control.MoveXY(w / 2 - ww + 275, h / 2 + 150)
        return pd

    def _sort_analyses(self):
        self.analyses.sort(key=lambda x:x.age)
#===============================================================================
# handlers
#===============================================================================
    def _update_selected_sample_fired(self):
        print 'asdf'
        ss = self.selected_sample
        if ss is not None:
            self.load_sample_ideogram()

            self._sort_analyses()

    def _update_selected_analysis_fired(self):
        sa = self.selected_analysis
        if sa is not None:
            dbr = sa.dbrecord
            dbr.load_graph()
            dbr.edit_traits()
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
        pr = self.project
        if pr:
            return [Sample(dbrecord=si
                           ) for si in pr.samples]
        return []

    @cached_property
    def _get_analyses(self):
        sample = self.selected_sample
        if sample:
            ans = [Analysis(dbrecord=IsotopeRecord(_dbrecord=ri))
                        for ln in sample.dbrecord.labnumbers
                            for ri in ln.analyses]
            if self.only_fusions:
                ans = filter(lambda x: x.step == '', ans)

            return ans
#            return sorted(ans, key=lambda x: x.age)
        return []

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
                           Item('display_omitted', label='Highlight Omitted Analyses',
                                enabled_when='include_omitted')
                           )
        grp = VGroup(HGroup(prj, spring, options_grp),
                     samples,
                     analyses
                     )
        v = View(grp,
                 width=500,
                 height=500,
                 resizable=True
                 )
        return v

if __name__ == '__main__':
    from globals import globalv
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
#        pd = MProgressDialog(max=n, size=(550, 15))
#        def open_progress():
#            pd.open()
#            (w, h) = wx.DisplaySize()
#            (ww, _hh) = pd.control.GetSize()
#            pd.control.MoveXY(w / 2 - ww + 275, h / 2 + 150)
#
#        do_later(open_progress)
##        time.sleep(0.1)
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
##        print time.time() - st
#        return ranalyses
#
#    def _load_analysis(self, queue, n, dbrecord=None, **kw):
#        from src.database.orms.isotope_orm import meas_AnalysisTable
#        sess = self.db.new_session()
#        q = sess.query(meas_AnalysisTable)
#        q = q.filter(meas_AnalysisTable.id == dbrecord._dbrecord.id)
#        dbr = q.one()
##        print id(dbr), dbr
#        dbrecord._dbrecord = dbr
#        a = Analysis(uuid=n,
#                     dbrecord=dbrecord,
#                         **kw)
#
#        if a.load_age():
#            queue.put(a)
##            self._analyses.append(a)
##        sess.expunge_all()
#        sess.close()
#        sess.remove()
