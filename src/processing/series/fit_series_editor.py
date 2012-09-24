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
from traits.api import HasTraits, Button, List, Str, Int, Instance, Property, Bool, Any, \
    DelegatesTo
from traitsui.api import View, Item, VGroup, HGroup, Spring, Label, Group, \
    spring
#============= standard library imports ========================
#============= local library imports  ==========================
from src.helpers.traitsui_shortcuts import listeditor
#from src.processing.blank_config import BlankConfig
from src.database.core.database_adapter import DatabaseAdapter
#from src.database.orms.isotope_orm import proc_BlanksTable
from src.loggable import Loggable
from src.processing.signal import Signal
#from src.processing.analysis import Signal
from src.database.orms.isotope_orm import AnalysisTable, MeasurementTable, AnalysisTypeTable, ExperimentTable

class FitSeriesEditor(Loggable):
    db = Instance(DatabaseAdapter)

    figure = Any
    workspace = DelegatesTo('figure')
    repo = DelegatesTo('figure')
    analyses = DelegatesTo('figure')

    apply = Button
    fit = Button
    revert = Button
    save = Button
    saveable = Bool(False)
    configs = List

#    note = Str
#    save_note = Button('Save')

    saveable = Bool(False)
    appliable = Property(depends_on='configs.save')

    _series_name = None
    _series_key = None
    _analysis_type = None

    def add(self, iso_keys):
        self.configs = [self.config_klass(label=iso)
                        for iso in iso_keys]


    def load_series(self):
        f = self.fits_figure
        sess = self.db.get_session()

        sanalyses = [bi
                  for a in self.analyses
                    for bi in self._get_db_results(a, sess)]

        sanalyses = list(set(sanalyses))
        if sanalyses:
            names, attrs = zip(*[(bi.path.filename, dict(dbresult=bi)) for bi in sanalyses])

            f.load_analyses(names, attrs=attrs, ispredictor=True)

        names = [ai.dbresult.path.filename for ai in self.analyses]

        gids = [1] * len(names)
        attrs = [dict(dbresult=ai.dbresult) for ai in self.analyses]
        #also load this analysis
        f.load_analyses(names, groupids=gids,
                        attrs=attrs)

#        self.db.reset()

    def _do_series_fit(self):
        sn = self._series_name
        self.info('Applying {} fits to analyses'.format(sn))
        db = self.db
        fs = self.fits_figure.fit_series
#        blanks = self.fits_figure.fit_series
        fit_analyses = [ba for ba in self.fits_figure.analyses
                            if ba.analysis_type == sn]
        analyses = self.analyses

        func_set = getattr(db, 'add_{}_set'.format(sn))

        for a in analyses:
            an = a.dbresult
            histories = an.blanks_histories
            histories = getattr(an, '{}_histories'.format(sn))
            phistory = histories[-1] if histories else None

            self.info('adding configs history for {}'.format(a.rid))
            func = getattr(db, 'add_{}'.format(sn))
            funchist = getattr(db, 'add_{}_history'.format(sn))
            func_set = getattr(db, 'add_{}_set'.format(sn))
            history = funchist(an)
            for fi in fs:
                isotope = fi.isotope
                fit = fi.fit
                self.info('adding configs. isotope={} fit={}'.format(isotope, fit))

                ni = func(history, isotope=isotope, fit=fit, use_set=True)

                self.info('adding configs set. nanalyses={}'.format(len(fit_analyses)))
                for fa in fit_analyses:
#                    db.add_blanks_set(ni, fa.dbresult)
                    func_set(ni, fa.dbresult)
                #copy configs from previous histories
                self._copy_from_previous(phistory, isotope)
        db.commit()
        for a in analyses:
            #reload figure's analyses
            a.load_from_database(dbr=a.dbresult)

        self.figure.refresh()

    def _apply(self, analysis):
        sn = self._series_name
        db = self.db

        an = analysis.dbresult
        histories = getattr(an, '{}_histories'.format(sn))
        phistory = histories[-1] if histories else None
        history = None

        funchist = getattr(db, 'add_{}_history'.format(sn))
        func = getattr(db, 'add_{}'.format(sn))
        for ci in self.configs:
            if ci.save:
                self.saveable = True
                l = ci.label
                uv = ci.value
                ue = ci.error
                k = '{}{}'.format(l, self._series_key)
                analysis.signals[k] = Signal(_value=uv, error=ue)
                if history is None:
                    self.info('adding {} history for {}'.format(sn, analysis.rid))

                    history = funchist(an)

                func(history, isotope=l, use_set=False,
                     user_value=uv, user_error=ue
                     )
                self.info('setting {} {}. {:0.5f} +/- {:0.5f}'.format(l, sn, uv, ue))

                self._copy_from_previous(phistory, history, l)

    def _copy_from_previous(self, phistory, chistory, isotope):
        if phistory is None:
            return

        sn = self._series_name
        db = self.db

        #copy configs from a previous history
        bs = getattr(phistory, sn)
        bss = [bi for bi in bs if bi.isotope != isotope]
        for bi in bss:
            li = bi.isotope
#            if li != isotope:
#                continue

            uv = bi.user_value
            ue = bi.user_error
            func = getattr(db, 'add_{}'.format(sn))
            func(chistory,
                  isotope=li,
                  use_set=bi.use_set,
                  user_value=uv,
                  user_error=ue
                  )

            self.info('copying {} {} from previous history. {:0.5f} +/- {:0.5f}'.format(li, sn, uv, ue))

    def _get_db_results(self, a, sess):
        at = self._analysis_type
        an = a.dbresult
        exp = an.experiment
        q = sess.query(AnalysisTable)
        q = q.join(ExperimentTable)
        q = q.join(MeasurementTable)
        q = q.join(AnalysisTypeTable)
        q = q.filter(AnalysisTypeTable.name == at)
        q = q.filter(ExperimentTable.id == exp.id)
        q = q.filter(AnalysisTable.id != an.id)
        return q.all()
#===============================================================================
# handler
#===============================================================================
    def _fit_fired(self):
        #open a figure with the default loaded configs
#        from figures.fits_figure import BlanksFigure
#        f = BlanksFigure(db=self.db,
#                   workspace=self.workspace,
#                   repo=self.repo)
        f = self.figure_klass(db=self.db,
                   workspace=self.workspace,
                   repo=self.repo)
        f.edit_traits()
        f.on_trait_change(self._do_series_fit, 'apply_event')
        self.fits_figure = f
        self.load_series()

    def _revert_fired(self):
        pass

    def _apply_fired(self):
        self.db.rollback()
        for a in self.analyses:
            self._apply(a)

    def _save_fired(self):
        '''
             add new blank history
             add configs row
        '''

        db = self.db
        self.info('committing {} to db'.format(self._series_name))
        db.commit()

#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        header = HGroup(Spring(springy=False, width=38),
                      Label('Value'),
                      Spring(springy=False, width=62),
                      Label('Error'),
                      Spring(springy=False, width=62),
                      Label('Save'),
                      )

        left = VGroup(
                     header,
                     listeditor('configs', height=125, width=600),
                     )
        right = HGroup(spring,
                       VGroup(
                              spring,
                              Item('apply',
                                   enabled_when='appliable',
                                   show_label=False),
                              Item('revert',
                                   enabled_when='0',
                                   show_label=False),
                              Item('save',
                                   enabled_when='saveable',
                                   show_label=False),
                              Item('fit', show_label=False),
                              spring
                            ),
                    )

#        v = View(HGroup(right, left))
        v = View(HGroup(left, right))
#        v = View(HGroup(left, spring , right))
        return v

    def _get_appliable(self):
        return [s for s in self.configs if s.save]

#    saveable = Property(depends_on='configs.save')
#    def _get_saveable(self):
#        return [s for s in self.configs if s.save]
#============= EOF =============================================
