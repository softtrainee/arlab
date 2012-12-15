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
from traits.api import HasTraits, List, Bool, Float, Str, Any, Instance
from traitsui.api import View, Item, TableEditor, HGroup, Group, VGroup, Spring, spring, \
    Label
#============= standard library imports ========================
import re
#============= local library imports  ==========================
from src.processing.analysis import Analysis
from src.helpers.traitsui_shortcuts import listeditor
from src.loggable import Loggable
from src.processing.signal import Blank, Background
from src.processing.corrections.fixed_value_correction import FixedValueCorrection
from src.processing.corrections.interpolation_correction import InterpolationCorrection


class CorrectionsManager(Loggable):
    '''
        base class for managers that apply corrections
        
        known subclasses blank_corrections_manager, background_corrections_manager
    '''
    db = Any
    analyses = List(Analysis)
    fixed_values = List(FixedValueCorrection)
    use_fixed_values = Bool(False)
    interpolation_correction = Instance(InterpolationCorrection)

    '''
        subclass needs to set the following values
    '''
    correction_name = None
    signal_klass = None
    signal_key = None
    def _analyses_changed(self):
        if self.analyses:
            #load a fit series
            self.interpolation_correction = InterpolationCorrection(analyses=self.analyses,
                                                                    kind=self.correction_name,
                                                                    db=self.db
                                                                    )
            self.interpolation_correction.load_predictors()

            #load fixed values
            self._load_fixed_values()

    def _load_fixed_values(self):
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

    def apply_correction(self):
        if self.use_fixed_values:
            for ai in self.analyses:
                history = self._add_history(ai)

                for fi in self.fixed_values:
                    if not fi.use_value:
                        continue

                    self._apply_fixed_correction(ai, history, fi.name, fi.value, fi.error)

        self.db.commit()

    def _add_history(self, analysis):
        dbrecord = analysis.dbrecord._dbrecord
        db = self.db

        #new history
        func = getattr(db, 'add_{}_history'.format(self.correction_name))
        history = func(dbrecord, user=db.save_username)
#        history = db.add_blanks_history(dbrecord, user=db.save_username)

        #set analysis' selected history
        sh = db.add_selected_histories(dbrecord)
        setattr(sh, 'selected_{}'.format(self.correction_name), history)
#        sh.selected_blanks = history
        return history

    def _apply_fixed_correction(self, analysis, history, isotope, value, error):
        dbrecord = analysis.dbrecord._dbrecord
        db = self.db

#        histories = dbrecord.blanks_histories
        histories = getattr(dbrecord, '{}_histories'.format(self.correction_name))
        phistory = histories[-1] if histories else None

        func = getattr(db, 'add_{}'.format(self.correction_name))
        func(history, isotope=isotope, use_set=False, user_value=value, user_error=error)
#        db.add_blanks(history, isotope=isotope, use_set=False, user_value=value, user_error=error)
        self._copy_from_previous(phistory, history, isotope)

        self._update_value(analysis, isotope, value, error)

    def _copy_from_previous(self, phistory, chistory, isotope):
        if phistory is None:
            return

        sn = self.correction_name
        db = self.db

        #copy configs from a previous history
        bs = getattr(phistory, sn)
        bss = [bi for bi in bs if bi.isotope != isotope]

        get_config = lambda x: next((ci for ci in self.fixed_values if ci.name == x))
        for bi in bss:
            li = bi.isotope
            if get_config(li).save:
                #dont copy from history if were going to save
                continue

            uv = bi.user_value
            ue = bi.user_error
            func = getattr(db, 'add_{}'.format(sn))
            func(chistory,
                  isotope=li,
                  use_set=bi.use_set,
                  user_value=uv,
                  user_error=ue
                  )

    def _update_value(self, analysis, isotope, value, error):
        b = self.signal_klass(_value=value, _error=error)
        key = '{}{}'.format(isotope, self.signal_key)
        analysis.dbrecord.signals[key] = b

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
        v = View(
                 VGroup(
                        HGroup(
                               Item('use_fixed_values'),
                               spring
                               ),
                        Group(
                            series_grp,
                            fixed_value_grp,
                            layout='tabbed'
                            )
                        ),
                 resizable=True,
                 buttons=['OK', 'Cancel']
                 )
        return v

class BlankCorrectionsManager(CorrectionsManager):
    correction_name = 'blanks'
    signal_key = 'bl'
    signal_klass = Blank

class BackgroundCorrectionsManager(CorrectionsManager):
    correction_name = 'backgrounds'
    signal_key = 'bg'
    signal_klass = Background

class DetectorIntercalibrationCorrectionsManager(CorrectionsManager):
    correction_name = 'detector_intercalibration'
    def _load_fixed_values(self):
        if not self.fixed_values:
            self.fixed_values = [FixedValueCorrection(name='ICFactor')]

#============= EOF =============================================