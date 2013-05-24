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
from traits.api import HasTraits, CStr, Str, CInt, Int, Dict, Tuple, List, Float, \
    TraitError, Property, Any, Either
from traitsui.api import View, Item, TableEditor
from src.loggable import Loggable
from src.experiment.utilities.identifier import make_runid, make_rid
#============= standard library imports ========================
#============= local library imports  ==========================

class ExportSpec(Loggable):
    rid = CStr
    aliquot = Either(CInt, Str)
    step = Str
    irradpos = CStr

    '''
        signals is a list of x,y points lists
        in same order as detectors
        e.g [zip(h1_xs, h1_ys), zip(ax_xs, ax_ys)]
        
    '''
    signals = List

    '''
        see signals
    '''
    baselines = List

    '''
        detectors is a list of (det, iso) tuples.
        e.g
        [('H1', 'Ar40'), ('AX', 'Ar39')]
        
    '''
    detectors = List

    blanks = List
    intercepts = Tuple

    baseline_fits = List
    signal_fits = List
    baseline_intercepts = List
    signal_intercepts = List

    spectrometer = Str
    extract_device = Str
    tray = Str
    position = Property(depends_on='_position')
    _position = Any

    power_requested = Float(0)
    power_achieved = Float(0)
    duration = Float(0)
    duration_at_request = Float(0)
    first_stage_delay = Int(0)
    second_stage_delay = Int(0)
    runscript_name = Str
    runscript_text = Str
    comment = Str

    def load_record(self, record):
        attrs = [
                 ('labnumber', 'labnumber'),
                 ('aliquot', 'aliquot'),
                 ('step', 'step'),
                 ('irradpos', 'labnumber'),
                 ('extract_device', 'extract_device'), ('tray', 'tray'),
                 ('position', 'position'), ('power_requested', 'extract_value'),
                 ('power_achieved', 'extract_value'), ('duration', 'duration'),
                 ('duration_at_request', 'duration'), ('first_stage_delay', 'cleanup'),
                 ('comment', 'comment'),
                 ]

        for exp_attr, run_attr in attrs:
            if hasattr(record, run_attr):
                try:
                    setattr(self, exp_attr, getattr(record, run_attr))
                except TraitError, e:
                    self.debug(e)

        if hasattr(record, 'ic_factor'):
            ic = record.ic_factor
            self.ic_factor_v = float(ic.nominal_value)
            self.ic_factor_e = float(ic.std_dev)
        else:
            self.debug('{} has no ic_factor attribute'.format(record,))

    def iter(self):
        return zip(self.detectors,
                   self.signals,
                   self.baselines,
                   self.blanks,
                   self.signal_intercepts,
                   self.baseline_intercepts,
                   self.signal_fits,
                   self.baseline_fits)

    @property
    def record_id(self):
        return make_rid(self.labnumber, self.aliquot, self.step)


    def _set_position(self, pos):
        if ',' in pos:
            self._position = list(map(int, pos.split(',')))
        else:
            self._position = pos
    def _get_position(self):
        return self._position
#============= EOF =============================================
