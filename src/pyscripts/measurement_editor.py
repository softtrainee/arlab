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
from traits.api import HasTraits, Int, Bool, String, Float, on_trait_change
from traitsui.api import View, Item, HGroup, VGroup, Group, spring
#============= standard library imports ========================
import os
import re
#============= local library imports  ==========================
from src.pyscripts.editor import PyScriptEditor
from src.paths import paths
from src.helpers.filetools import str_to_bool

#===============================================================================
# counts
#===============================================================================
MULTICOLLECT_NCOUNTS_REGEX = re.compile(r'(MULTICOLLECT_COUNTS) *= *\d+$')
#===============================================================================
# baseline
#===============================================================================
BASELINE_NCOUNTS_REGEX = re.compile(r'(BASELINE_COUNTS) *= *\d+$')
BASELINE_DETECTOR_REGEX = re.compile(r'(BASELINE_DETECTOR) *= *')
BASELINE_MASS_REGEX = re.compile(r'(BASELINE_MASS) *= *')
BASELINE_BEFORE_REGEX = re.compile(r'(BASELINE_BEFORE) *= *')
BASELINE_AFTER_REGEX = re.compile(r'(BASELINE_AFTER) *= *')
BASELINE_SETTLING_TIME_REGEX = re.compile(r'(BASELINE_SETTLING_TIME) *= *')

#===============================================================================
# peak center
#===============================================================================
PEAK_CENTER_BEFORE_REGEX = re.compile(r'(PEAK_CENTER_BEFORE) *= *')
PEAK_CENTER_AFTER_REGEX = re.compile(r'(PEAK_CENTER_AFTER) *= *')
PEAK_CENTER_DETECTOR_REGEX = re.compile(r"(PEAK_CENTER_DETECTOR) *= *")
PEAK_CENTER_ISOTOPE_REGEX = re.compile(r"(PEAK_CENTER_ISOTOPE) *= *")
#===============================================================================
# equilibration
#===============================================================================
EQ_TIME_REGEX = re.compile(r"(EQ_TIME) *= *")
EQ_INLET_REGEX = re.compile(r"(INLET) *= *")
EQ_OUTLET_REGEX = re.compile(r"(OUTLET) *= *")
EQ_DELAY_REGEX = re.compile(r"(EQ_DELAY) *= *")


PARAMS = dict(
             peak_center_before=(PEAK_CENTER_BEFORE_REGEX, 'PEAK_CENTER_BEFORE= {}'),
             peak_center_after=(PEAK_CENTER_AFTER_REGEX, 'PEAK_CENTER_AFTER= {}'),
             peak_center_detector=(PEAK_CENTER_DETECTOR_REGEX, "PEAK_CENTER_DETECTOR= '{}'"),
             peak_center_isotope=(PEAK_CENTER_ISOTOPE_REGEX, "PEAK_CENTER_ISOTOPE= '{}'"),
             multicollect_ncounts=(MULTICOLLECT_NCOUNTS_REGEX, 'MULTICOLLECT_COUNTS= {}'),


             baseline_before=(BASELINE_BEFORE_REGEX, 'BASELINE_BEFORE= {}'),
             baseline_after=(BASELINE_AFTER_REGEX, 'BASELINE_AFTER= {}'),
             baseline_ncounts=(BASELINE_NCOUNTS_REGEX, 'BASELINE_COUNTS= {}'),
             baseline_detector=(BASELINE_DETECTOR_REGEX, "BASELINE_DETECTOR= '{}'"),
             baseline_mass=(BASELINE_MASS_REGEX, 'BASELINE_MASS= {}'),
             baseline_settling_time=(BASELINE_SETTLING_TIME_REGEX, 'BASELINE_SETTLING_TIME= {}'),

             eq_time=(EQ_TIME_REGEX, 'EQ_TIME= {}'),
             eq_inlet=(EQ_INLET_REGEX, "INLET= '{}'"),
             eq_outlet=(EQ_OUTLET_REGEX, "OUTLET= '{}'"),
             eq_delay=(EQ_DELAY_REGEX, 'EQ_DELAY= {}'),
             )


class MeasurementPyScriptEditor(PyScriptEditor):
    _kind = 'Measurement'
    #===========================================================================
    # counts
    #===========================================================================
    multicollect_ncounts = Int(100)

    #===========================================================================
    # baselines
    #===========================================================================
    baseline_ncounts = Int(100)
    baseline_detector = String
    baseline_mass = Float
    baseline_before = Bool
    baseline_after = Bool
    baseline_settling_time = Int(3)

    #===========================================================================
    # peak center
    #===========================================================================
    peak_center_before = Bool
    peak_center_after = Bool
    peak_center_isotope = String
    peak_center_detector = String

    #===========================================================================
    # equilibration
    #===========================================================================
    eq_time = Float
    eq_outlet = String
    eq_inlet = String
    eq_delay = Float

    def _get_parameters_group(self):

        multicollect_grp = Group(
                                 Item('multicollect_ncounts', label='Counts',
                                      tooltip='Number of data points to collect'
                                      ),
                                 label='Multicollect',
                                 show_border=True
                                 )
        baseline_grp = Group(
                             Item('baseline_before', label='Baselines at Start'),
                             Item('baseline_after', label='Baselines at End'),
                             Item('baseline_ncounts',
                                  tooltip='Number of baseline data points to collect',
                                  label='Counts'),
                             Item('baseline_detector', label='Detector'),
                             Item('baseline_settling_time',
                                  label='Delay (s)',
                                  tooltip='Wait "Delay" seconds after setting magnet to baseline position'
                                  ),
                             Item('baseline_mass', label='Mass'),
                             label='Baseline',
                             show_border=True
                             )

        peak_center_grp = Group(
                              Item('peak_center_before', label='Peak Center at Start'),
                              Item('peak_center_after', label='Peak Center at End'),
                              Item('peak_center_detector',
                                   label='Detector',
                                   enabled_when='peak_center_before or peak_center_after'
                                   ),
                              Item('peak_center_isotope',
                                   label='Isotope',
                                   enabled_when='peak_center_before or peak_center_after'
                                   ),
                              label='Peak Center',
                              show_border=True)

        equilibration_grp = Group(
                                Item('eq_time', label='Time (s)'),
                                Item('eq_outlet', label='Ion Pump Valve'),
                                Item('eq_delay', label='Delay (s)',
                                     tooltip='Wait "Delay" seconds before opening the Inlet Valve'
                                     ),
                                Item('eq_inlet', label='Inlet Valve'),
                                label='Equilibration',
                                show_border=True
                                )

        return Group(
                     HGroup(
                            VGroup(
                                 multicollect_grp,
                                 baseline_grp,
                                 peak_center_grp,
                                 equilibration_grp),
                            spring,
                            ),

                     label='Parameters')

    def _parse(self):
        str_to_str = lambda x: x.replace("'", '').replace('"', '')
        for li in self.body.split('\n'):
            if self._extract_parameter(li, MULTICOLLECT_NCOUNTS_REGEX, 'multicollect_ncounts', cast=int):
                continue

            #===================================================================
            # baselines
            #===================================================================
            if self._extract_parameter(li, BASELINE_BEFORE_REGEX, 'baseline_before', cast=str_to_bool):
                continue
            if self._extract_parameter(li, BASELINE_AFTER_REGEX, 'baseline_after', cast=str_to_bool):
                continue
            if self._extract_parameter(li, BASELINE_NCOUNTS_REGEX, 'baseline_ncounts', cast=int):
                continue
            if self._extract_parameter(li, BASELINE_DETECTOR_REGEX, 'baseline_detector', cast=str_to_str):
                continue
            if self._extract_parameter(li, BASELINE_MASS_REGEX, 'baseline_mass', cast=float):
                continue

            #===================================================================
            # peak center
            #===================================================================
            if self._extract_parameter(li, PEAK_CENTER_BEFORE_REGEX, 'peak_center_before', cast=str_to_bool):
                continue
            if self._extract_parameter(li, PEAK_CENTER_AFTER_REGEX, 'peak_center_after', cast=str_to_bool):
                continue
            if self._extract_parameter(li, PEAK_CENTER_DETECTOR_REGEX, 'peak_center_detector', cast=str_to_str):
                continue
            if self._extract_parameter(li, PEAK_CENTER_ISOTOPE_REGEX, 'peak_center_isotope', cast=str_to_str):
                continue

            #===================================================================
            # equilibration
            #===================================================================
            if self._extract_parameter(li, EQ_TIME_REGEX, 'eq_time', cast=float):
                continue
            if self._extract_parameter(li, EQ_INLET_REGEX, 'eq_inlet', cast=str_to_str):
                continue
            if self._extract_parameter(li, EQ_OUTLET_REGEX, 'eq_outlet', cast=str_to_str):
                continue
            if self._extract_parameter(li, EQ_DELAY_REGEX, 'eq_delay', cast=float):
                continue

    def _extract_parameter(self, line, regex, attr, cast=None):
        if regex.match(line):
            _, v = line.split('=')
            v = v.strip()
            if cast:
                v = cast(v)
            setattr(self, attr, v)

    @on_trait_change('peak_center_+, eq_+, multicollect_ncounts, baseline_+')
    def _update_value(self, name, new):
        regex = self._get_regex(name)
        nv = self._get_new_value(name, new)
        return self._modify_body(regex, nv)

    def _get_regex(self, name):
        return PARAMS[name][0]

    def _get_new_value(self, name, new):
        return PARAMS[name][1].format(new)

    def _modify_body(self, regex, nv):
        ostr = []
        modified = False
        for li in self.body.split('\n'):
            if regex.match(li.strip()):
                ostr.append(nv)
                modified = True
            else:
                ostr.append(li)

        self.body = '\n'.join(ostr)

        return modified

if __name__ == '__main__':
    from launchers.helpers import build_version
    build_version('_experiment')
    from src.helpers.logger_setup import logging_setup
    logging_setup('scripts')

    s = MeasurementPyScriptEditor()

    p = os.path.join(paths.scripts_dir, 'measurement', 'jan_unknown.py')
    s.open_script(path=p)
    s.configure_traits()
#============= EOF =============================================
