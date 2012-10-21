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
#from traits.api import HasTraits, Button, List, Str, Int, Instance, Property, Bool, Any, \
#    DelegatesTo
#from traitsui.api import View, Item, VGroup, HGroup, Spring, Label, Group, \
#    spring
#============= standard library imports ========================
#============= local library imports  ==========================
#from src.helpers.traitsui_shortcuts import listeditor
from src.experiment.processing.series.blank_config import BlankConfig
#from src.database.core.database_adapter import DatabaseAdapter
#from src.database.orms.isotope_orm import proc_BlanksTable
#from src.loggable import Loggable
#from src.experiment.processing.analysis import Signal
from src.experiment.processing.series.fit_series_editor import FitSeriesEditor
from src.experiment.processing.figures.blanks_figure import BlanksFigure
#from src.database.orms.isotope_orm import AnalysisTable, MeasurementTable, AnalysisTypeTable, ExperimentTable

#@todo: add notes to configs history table
#@todo: save notes to configs history table

#class BlanksEditor(Loggable):
class BlanksEditor(FitSeriesEditor):
    config_klass = BlankConfig
    figure_klass = BlanksFigure
    _series_name = 'blanks'
    _series_key = 'bl'
    _analysis_type = 'blank'


#    db = Instance(DatabaseAdapter)
#
#    figure = Any
#    workspace = DelegatesTo('figure')
#    repo = DelegatesTo('figure')
#    analyses = DelegatesTo('figure')

#    apply_blanks = Button
#    fit_blanks = Button
#    revert_blanks = Button
#    save_blanks = Button

#    configs = List
#
##    note = Str
##    save_note = Button('Save')
#
#    saveable = Bool(False)
#    appliable = Property(depends_on='configs.save')
#
#    def _get_appliable(self):
#        return [s for s in self.configs if s.save]
##    saveable = Property(depends_on='configs.save')
##    def _get_saveable(self):
##        return [s for s in self.configs if s.save]
#
#    def add(self, iso_keys):
#        self.configs = [self.config_klass(label=iso)
#                        for iso in iso_keys]

#===============================================================================
# handlers
#===============================================================================

#    def _fit_fired(self):
#        #open a figure with the default loaded configs
##        from figures.fits_figure import BlanksFigure
##        f = BlanksFigure(db=self.db,
##                   workspace=self.workspace,
##                   repo=self.repo)
#        f = self.figure_klass(db=self.db,
#                   workspace=self.workspace,
#                   repo=self.repo)
#        f.edit_traits()
#        f.on_trait_change(self._fit_blanks, 'apply_blanks_event')
#        self.fits_figure = f
#        self._load()
#    def _get_db_results(self, a, sess):
#        an = a.dbrecord
#        exp = an.experiment
#        q = sess.query(AnalysisTable)
#        q = q.join(ExperimentTable)
#        q = q.join(MeasurementTable)
#        q = q.join(AnalysisTypeTable)
#        q = q.filter(AnalysisTypeTable.name == 'blank')
#        q = q.filter(ExperimentTable.id == exp.id)
#        q = q.filter(AnalysisTable.id != an.id)
#        return q.all()

#    def load_series(self):
#
#        f = self.fits_figure
#        sess = self.db.get_session()
#        analyses = [bi
#                  for a in self.analyses
#                    for bi in self._get_db_results(a, sess)]
#        self._load(analyses)
##    def _load(self, blanks):
##        f = self.fits_figure
##        sess = self.db.get_session()
##        from src.database.orms.isotope_orm import AnalysisTable, MeasurementTable, AnalysisTypeTable, ExperimentTable
#        #get configs associated with these analyses base on the experiment
##        names = []
##        attrs = []
##        def get_blanks(a):
##            an = a.dbrecord
##            exp = an.experiment
##            q = sess.query(AnalysisTable)
##            q = q.join(ExperimentTable)
##            q = q.join(MeasurementTable)
##            q = q.join(AnalysisTypeTable)
##            q = q.filter(AnalysisTypeTable.name == 'blank')
##            q = q.filter(ExperimentTable.id == exp.id)
##            q = q.filter(AnalysisTable.id != an.id)
##            return q.all()
#
##        blanks = [bi
##                  for a in self.analyses
##                    for bi in self._get_db_results(a, sess)]
#
#        blanks = list(set(blanks))
#        names, attrs = zip(*[(bi.path.filename, dict(dbrecord=bi)) for bi in blanks])
#
#        f.load_analyses(names, attrs=attrs)
#
#        names = [ai.dbrecord.path.filename for ai in self.analyses]
#        gids = [1] * len(names)
#        attrs = [dict(dbrecord=ai.dbrecord) for ai in self.analyses]
#        #also load this analysis
#        f.load_analyses(names, groupids=gids,
#                        attrs=attrs)


#    def _do_series_fit(self):
#        self.info('Applying blank fits to analyses')
#        db = self.db
#
#        blanks = self.fits_figure.fit_series
#        fit_analyses = [ba for ba in self.fits_figure.analyses if ba.analysis_type == 'blank']
#        analyses = self.analyses
#        for a in analyses:
#            an = a.dbrecord
#            histories = an.blanks_histories
#            phistory = histories[-1] if histories else None
#
#            self.info('adding configs history for {}'.format(a.rid))
#            history = db.add_blanks_history(an)
#            for bi in blanks:
#
#                isotope = bi.label
#                fit = bi.fit
##                a.age_dirty = True
#                self.info('adding configs. isotope={} fit={}'.format(isotope, fit))
#                bl = db.add_blanks(history,
#                              isotope=isotope,
#                              fit=fit,
#                              use_set=True)
#
#                self.info('adding configs set. nanalyses={}'.format(len(fit_analyses)))
#                for fa in fit_analyses:
#                    db.add_blanks_set(bl, fa.dbrecord)
#
#                #copy configs from previous histories
#                self._copy_from_previous(phistory, isotope)
#
#        db.commit()
#
#        for a in analyses:
#            #reload figure's analyses
#            a.load_from_database(dbr=a.dbrecord)
#
#        self.figure.refresh()

#    def _revert_blanks_fired(self):
#        pass
#
#    def _save_blanks_fired(self):
#        '''
#             add new blank history
#             add configs row
#        '''
#
#        db = self.db
#        self.info('committing configs to db')
#        db.commit()

#    def _apply_fired(self):
#        for a in self.analyses:
#            self._apply(a)
#    def _apply(self, analysis):
#        db = self.db
#        an = analysis.dbrecord
#        histories = an.blanks_histories
#        phistory = histories[-1] if histories else None
#        history = None
#        for bci in self.configs:
#            if bci.save:
#                self.saveable = True
#                l = bci.label
#                uv = bci.value
#                ue = bci.error
#
#                analysis.signals['{}bl'.format(l)] = Signal(_value=uv, _error=ue)
#                analysis.age_dirty = True
#
#                if history is None:
#                    self.info('adding configs history for {}'.format(analysis.rid))
#                    history = db.add_blanks_history(an)
#
#                db.add_blanks(history,
#                                   isotope=l,
#                                   use_set=False,
#                                   user_value=uv, user_error=ue)
#                self.info('setting {} blank. {:0.5f} +/- {:0.5f}'.format(l, uv, ue))
#
#                self._copy_from_previous(phistory, l)

#    def _copy_from_previous(self, history, isotope):
#        if history is None:
#            return
#
#        sn = self.__series_name
#        db = self.db
#        #copy configs from a previous history
#        for bi in history.configs:
#            li = bi.isotope
#            if li == isotope:
#                continue
#
#            uv = bi.user_value
#            ue = bi.user_error
#            func = getattr(db, 'add_{}s'.format(sn))
#            func(history,
#                  isotope=li,
#                  use_set=bi.use_set,
#                  user_value=uv,
#                  user_error=ue
#                  )
#            
#            self.info('copying {} {} from previous history. {:0.5f} +/- {:0.5f}'.format(li, sn, uv, ue))

#===============================================================================
# views
#===============================================================================
#    def traits_view(self):
#        header = HGroup(Spring(springy=False, width=38),
#                      Label('Value'),
#                      Spring(springy=False, width=62),
#                      Label('Error'),
#                      Spring(springy=False, width=62),
#                      Label('Save'),
#                      )
#
#        left = VGroup(
#                     header,
#                     listeditor('configs', height=125),
#                     )
#        right = HGroup(
#                       Item('apply_blanks',
#                           enabled_when='appliable',
#                           show_label=False),
#                       Item('revert_blanks',
#                                       enabled_when='0',
#                                       show_label=False,
#                                       ),
#                      Item('save_blanks',
#                           enabled_when='saveable',
#                           show_label=False),
#                      Item('fit_blanks', show_label=False)
#                    )
#
#        v = View(HGroup(left, right))
##        v = View(right)
#        return v
#============= EOF =============================================
