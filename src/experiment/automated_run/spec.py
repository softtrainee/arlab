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
from traits.api import HasTraits, Str, Int, Bool, Float, Property, Enum
from traitsui.api import View, Item, TableEditor
from src.experiment.automated_run.automated_run import AutomatedRun
from src.constants import SCRIPT_KEYS
#============= standard library imports ========================
#============= local library imports  ==========================

class AutomatedRunSpec(HasTraits):
    state = Property(depends_on='_state')
    _state = Enum('not run', 'extraction',
                 'measurement', 'success', 'fail', 'truncate')
    mass_spectrometer = Str
    extract_device = Str
    labnumber = Str
    aliquot = Int
    measurement_script = Str
    post_measurement_script = Str
    post_equilibration_script = Str
    extraction_script = Str
    user_defined_aliquot = False

    skip = Bool(False)

    extract_group = Int
    extract_value = Float
    extract_units = Str
    position = Str
    duration = Float
    cleanup = Float
    sample = Str

    weight = Float
    comment = Str
    def to_string(self):
        attrs = ['labnumber', 'aliquot',
                   'extract_value', 'extract_units',
                   'position', 'duration', 'cleanup',
                   'mass_spectrometer', 'extract_device',
                   'extraction_script', 'measurement_script',
                   'post_equilibration_script', 'post_measurement_script'
                   ]
        return ','.join(map(str, self.to_string_attrs(attrs)))

    def get_estimated_duration(self):
        return self.duration + self.cleanup

    def make_run(self):
        arun = AutomatedRun()
        for ai in ('labnumber', 'aliquot',
                   'extract_value', 'extract_units',
                   'position', 'duration', 'cleanup',
                   'mass_spectrometer', 'extract_device'
                   ):

            setattr(arun, ai, getattr(self, ai))

        for si in SCRIPT_KEYS:
            setattr(arun.script_info, '{}_script_name'.format(si),
                    getattr(self, '{}_script'.format(si)))

        return arun

    def load(self, script_info, params):
        for k, v in script_info.iteritems():
            setattr(self, '{}_script'.format(k), v)

        for k, v in params.iteritems():
#            print 'param', k, v
            if hasattr(self, k):
                setattr(self, k, v)

    def to_string_attrs(self, attrs):
        def get_attr(attrname):
            if attrname == 'labnumber':
                if self.user_defined_aliquot:
                    v = '{}-{}'.format(self.labnumber, self.aliquot)
                else:
                    v = self.labnumber
            else:
                try:
                    v = getattr(self, attrname)
                except AttributeError, e:
                    v = ''

            return v

        return [get_attr(ai) for ai in attrs]

#===============================================================================
# property get/set
#===============================================================================
    def _get_state(self):
        return self._state

    def _set_state(self, s):
        if self._state != 'truncate':
            self._state = s

#============= EOF =============================================
