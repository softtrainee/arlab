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
from traits.api import List, Bool, Any, Instance, Button, Property, \
    cached_property
from traitsui.api import View, Item, HGroup, Group, VGroup, Spring, spring, \
    Label, TabularEditor
from traitsui.menu import Action

#============= standard library imports ========================
import re
#============= local library imports  ==========================
from src.processing.analysis import Analysis
from src.helpers.traitsui_shortcuts import listeditor

# from src.processing.signal import Blank, Background, Signal
from src.processing.corrections.fixed_value_correction import FixedValueCorrection
from src.processing.corrections.interpolation_correction import InterpolationCorrection, \
    DetectorIntercalibrationInterpolationCorrection
# from src.viewable import Viewable
from src.saveable import Saveable
from traitsui.tabular_adapter import TabularAdapter
from src.processing.isotope import Isotope


class GroupedAnalysisAdapter(TabularAdapter):
    columns = [
               ('Analysis ID', 'record_id'),
               ('Status', 'status'),
#               ('Temp. Status', 'temp_status'),
               ]

    def get_bg_color(self, obj, trait, row):
        bgcolor = self.item.bgcolor
        if bgcolor is None:
            bgcolor = 'white'

        if self.item.status == 1:
            return 0xFF8080
        elif self.item.temp_status == 1:
            return 0xFFCC00

        return bgcolor

class CorrectionsManager(Saveable):
    '''
        base class for managers that apply corrections
        
        known subclasses blank_corrections_manager, background_corrections_manager
    '''
    db = Any
    processing_manager = Any
    analyses = List(Analysis)
    all_analyses = Property(List(Analysis), depends_on='analyses')

    fixed_values = List(FixedValueCorrection)
    use_fixed_values = Bool(False)
    interpolation_correction = Instance(InterpolationCorrection)
    interpolation_correction_klass = InterpolationCorrection
    edit_predictors = Button('Edit')
    dclicked = Any
    selected = Any
    '''
        subclass needs to set the following values
    '''
    correction_name = None
    isotope_klass = Isotope

#    signal_key = None
    isotope_name = 'isotope'
    analysis_type = None

    def close(self, isok):
        if isok:
            self.interpolation_correction.dump_fits()
        return True

    def apply(self):
        self.apply_correction()

    def apply_correction(self):
        if self.use_fixed_values:
            for ai in self.analyses:
                history = None
                for fi in self.fixed_values:
                    if not fi.use:
                        continue

                    if history is None:
                        history = self._add_history(ai)

                    self._apply_fixed_correction(ai, history, fi.name, fi.value, fi.error)
        else:
            self._apply_interpolation_correction()

        self.db.commit()
#===============================================================================
# handlers
#===============================================================================
    def _dclicked_changed(self):
        selector = self.db.selector
        selector.open_record(self.selected.isotope_record)

    def _edit_predictors_fired(self):

        # set the selector.selected_records to the predictors
        ps = self.interpolation_correction.predictors
        selector = self.processing_manager.selector_manager
        selector.selected_records = [ri.isotope_record for ri in ps]
        ans = self.processing_manager.gather_data()
        if ans:
            self.interpolation_correction._predictors = ans
            self.interpolation_correction.dirty = True
            self.interpolation_correction.refresh()

    def _analyses_changed(self):
        if self.analyses:
            # load a fit series
            self.interpolation_correction = self.interpolation_correction_klass(analyses=self.analyses,
                                                                    kind=self.correction_name,
                                                                    isotope_klass=self.isotope_klass,
                                                                    isotope_name=self.isotope_name,
                                                                    analysis_type=self.analysis_type,
                                                                    db=self.db,
                                                                    )
            self.interpolation_correction.load_fits(self._get_isotope_names())
            self.interpolation_correction.load_predictors()

            # load fixed values
            self._load_fixed_values()

    def _apply_interpolation_correction(self):
#        db = self.db
#        func = getattr(db, 'add_{}'.format(self.correction_name))
#        func2 = getattr(db, 'add_{}_set'.format(self.correction_name))
        for ai in self.analyses:

            histories = getattr(ai.dbrecord, '{}_histories'.format(self.correction_name))
            phistory = histories[-1] if histories else None

            history = self._add_history(ai)
            for si in self.interpolation_correction.fits:
                if not si.use:
                    self._apply_fixed_value_correction(phistory, history, si)
                else:
                    self._apply_correction(history, ai, si)

    def _apply_fixed_value_correction(self, phistory, history, si):
        db = self.db
        if phistory:
            bs = getattr(phistory, self.correction_name)
            bs = reversed(bs)
            prev = next((bi for bi in bs if bi.isotope == si.name), None)
            if prev:
                uv = prev.user_value
                ue = prev.user_error
                func = getattr(db, 'add_{}'.format(self.correction_name))
                func(history,
                      isotope=prev.isotope,
                      fit=prev.fit,
                      user_value=uv,
                      user_error=ue
                      )

#    def _apply_set_correction(self, history, ai, si):
#        db = self.db
#        func = getattr(db, 'add_{}'.format(self.correction_name))
#        func2 = getattr(db, 'add_{}_set'.format(self.correction_name))
# #        ss = ai.signals['{}{}'.format(si.name, self.signal_key)]
# #        ss=ai.isotopes
#
#        ss = self._get_isotope_value(ai, si.name)
#
#        item = func(history, isotope=si.name,
#                    user_value=ss.value,
#                    user_error=ss.error,
# #                                use_set=True,
#                    fit=si.fit)
#        ps = self.interpolation_correction.predictors
#        if ps:
#            for pi in ps:
#                func2(item, pi.dbrecord)

    @cached_property
    def _get_all_analyses(self):
        ans = self.analyses
        prs = self.interpolation_correction.predictors
        for pi in prs:
            pi.bgcolor = 0x99CCFF

        ts = ans + prs
        ts = sorted(ts, key=lambda x: x.timestamp)
        return ts

    def _get_isotope_names(self):
        keys = None
        for a in self.analyses:
            nkeys = a.isotope_keys
            if keys is None:
                keys = set(nkeys)
            else:
                keys = set(nkeys).intersection(keys)

        keys = sorted(keys,
                      key=lambda x: re.sub('\D', '', x),
                      reverse=True
                      )
        return keys

    def _add_history(self, analysis):
        dbrecord = analysis.dbrecord
        db = self.db

        # new history
        func = getattr(db, 'add_{}_history'.format(self.correction_name))
        history = func(dbrecord, user=db.save_username)
#        history = db.add_blanks_history(dbrecord, user=db.save_username)

        # set analysis' selected history
        sh = db.add_selected_histories(dbrecord)
        setattr(sh, 'selected_{}'.format(self.correction_name), history)
#        sh.selected_blanks = history
        return history

    def _apply_fixed_correction(self, analysis, history, isotope, value, error):
#        dbrecord = analysis.dbrecord
        db = self.db

#        histories = dbrecord.blanks_histories
#        histories = getattr(dbrecord, '{}_histories'.format(self.correction_name))
#        phistory = histories[-1] if histories else None

        func = getattr(db, 'add_{}'.format(self.correction_name))
        func(history, isotope=isotope, use_set=False, user_value=value, user_error=error)
#        db.add_blanks(history, isotope=isotope, use_set=False, user_value=value, user_error=error)

        # need to reimplement copy from previous
#        self._copy_from_previous(phistory, history, isotope)


        self._update_value(analysis, isotope, value, error)

#    def _copy_from_previous(self, phistory, chistory, isotope):
#        if phistory is None:
#            return
#
#        sn = self.correction_name
#        db = self.db
#
#        #copy configs from a previous history
#        bs = getattr(phistory, sn)
#        bs = reversed(bs)
#
#        prev_values = []
#        bb = []
#        for bi in bs:
#            if bi.isotope in prev_values:
#                continue
#            elif bi.isotope != isotope:
#                prev_values.append(bi.isotope)
#                bb.append(bi)
#
# #        bss = [bi for bi in bs if bi.isotope != isotope]
# #        get_config = lambda x: next((ci for ci in self.fixed_values if ci.name == x))
#        for bi in bb:
#
# #            print bi, li
# #            if get_config(li).save:
# #                #dont copy from history if were going to save
# #                continue
#
#            uv = bi.user_value
#            ue = bi.user_error
#            func = getattr(db, 'add_{}'.format(sn))
#            func(chistory,
#                  isotope=bi.isotope,
#                  fit=bi.fit,
#                  use_set=bi.use_set,
#                  user_value=uv,
#                  user_error=ue
#                  )

    def _update_value(self, analysis, isotope, value, error):
#        b = Isotope(_value=value, _error=error)
#        key = '{}{}'.format(isotope, self.signal_key)
        func = getattr(analysis, 'set_{}'.format(self.isotope_name))
        func(isotope, value, error)
#        analysis.isotopes[key] = b

    def _load_fixed_values(self):
        keys = self._get_isotope_names()
        nfixed_values = [FixedValueCorrection(name=ki) for ki in keys]
        if self.fixed_values:
            nn = []
            for ni in nfixed_values:
                obj = next((fi for fi in self.fixed_values
                            if fi.name == ni.name), None)
                if obj:
                    nn.append(obj)
                else:
                    nn.append(ni)
        else:
            nn = nfixed_values
        self.fixed_values = nn

    def traits_view(self):
        fixed_value_grp = Group(VGroup(
                                       HGroup(spring, Label('Value'),
                                              Spring(width=65, springy=False),
                                              Label('Error'),
                                              spring
                                              ),
                                       listeditor('fixed_values')
                                       ),
                                label='Fixed Values'
                               )
        series_grp = Group(
                           Item('interpolation_correction', show_label=False, style='custom'),
                           label='Series')
        table_grp = Group(
                        Item('all_analyses', show_label=False, style='custom',
                             editor=TabularEditor(adapter=GroupedAnalysisAdapter(),
                                                  editable=False,
                                                  dclicked='dclicked',
                                                  selected='selected'
                                                  )
                             ),
                        label='Analyses')
        v = View(
                 VGroup(
                        HGroup(
                               Item('use_fixed_values'),
                               spring,
                               Item('edit_predictors', show_label=False)
                               ),
                        Group(
                            series_grp,
                            table_grp,
                            fixed_value_grp,
                            layout='tabbed'
                            )
                        ),
                 handler=self.handler_klass,
                 title=self.title,
                 resizable=True,
                 buttons=[Action(name='Apply', action='apply')]
                 )
        return v

class BlankCorrectionsManager(CorrectionsManager):
    correction_name = 'blanks'
#    signal_key = 'bl'
#    signal_klass = Blank
    isotope_name = 'blank'
    analysis_type = 'blank'
    title = 'Set Blanks'
    def _get_isotope_value(self, an, name):
        if an.isotopes.has_key(name):
            iso = an.isotopes[name]
            return iso.blank

    def _apply_correction(self, history, ai, si):
        ss = ai.isotopes[si.name]
        item = self.db.add_blanks(history,
                    isotope=si.name,
                    user_value=float(ss.blank.value),
                    user_error=float(ss.blank.error),
                    fit=si.fit)
        ps = self.interpolation_correction.predictors
        if ps:
            for pi in ps:
                self.db.add_blanks_set(item, pi.dbrecord)

class BackgroundCorrectionsManager(CorrectionsManager):
    correction_name = 'backgrounds'
#    signal_key = 'bg'
#    signal_klass = Background
    isotope_name = 'background'

    title = 'Set Backgrounds'
    analysis_type = 'background'
    def _get_isotope_value(self, an, name):
        if an.isotopes.has_key(name):
            iso = an.isotopes[name]
            return iso.background



class DetectorIntercalibrationCorrectionsManager(CorrectionsManager):
    title = 'Set Detector Intercalibration'
    correction_name = 'detector_intercalibration'
    analysis_type = 'air'


    interpolation_correction_klass = DetectorIntercalibrationInterpolationCorrection
    def _load_fixed_values(self):
        if not self.fixed_values:
            self.fixed_values = [FixedValueCorrection(name='ICFactor')]

    def _apply_fixed_correction(self, analysis, history, isotope, value, error):
        db = self.db
        func = getattr(db, 'add_{}'.format(self.correction_name))
        func(history, 'CDD', user_value=value, user_error=error)
        self._update_value(analysis, isotope, value, error)

    def _apply_fixed_value_correction(self, phistory, history, si):
        if phistory:
            bs = phistory.detector_intercalibration
            bs = reversed(bs)
            prev = next((bi for bi in bs if bi.detector.name == 'CDD'), None)
            if prev:
                uv = prev.user_value
                ue = prev.user_error
                func = self.db.add_detector_intercalibration
                func(history,
                      fit=prev.fit,
                      user_value=uv,
                      user_error=ue
                      )

    def _apply_correction(self, history, ai, si):
        ss = ai.isotopes[si.name]
        item = self.db.add_detector_intercalibration(history, 'CDD',
                    user_value=float(ss.value),
                    user_error=float(ss.error),
                    fit=si.fit)
        ps = self.interpolation_correction.predictors
        if ps:
            for pi in ps:
                self.db.add_detector_intercalibration_set(item, pi.dbrecord)
#============= EOF =============================================
