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
from numpy import array
from traits.api import CStr, Str, CInt, Float, \
    TraitError, Property, Any, Either, Instance, Dict
from uncertainties import ufloat
from src.loggable import Loggable
from src.experiment.utilities.identifier import make_rid
#============= standard library imports ========================
#============= local library imports  ==========================
from src.managers.data_managers.h5_data_manager import H5DataManager


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
    #signals = List

    '''
        see signals
    '''
    #baselines = List

    '''
        detectors is a list of (det, iso) tuples.
        e.g
        [('H1', 'Ar40'), ('AX', 'Ar39')]
        
    '''
    #detectors = List

    blanks = Dict
    #intercepts = Tuple

    #baseline_fits = List
    signal_fits = Dict
    #baseline_intercepts = List
    signal_intercepts = Dict

    spectrometer = Str
    extract_device = Str
    tray = Str
    position = Property(depends_on='_position')
    _position = Any

    power_requested = Float(0)
    power_achieved = Float(0)
    duration = Float(0)
    duration_at_request = Float(0)
    first_stage_delay = CInt(0)
    second_stage_delay = CInt(0)
    runscript_name = Str
    runscript_text = Str
    comment = Str

    data_path = Str
    data_manager = Instance(H5DataManager, ())

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
            if hasattr(record.spec, run_attr):
                try:
                    setattr(self, exp_attr, getattr(record.spec, run_attr))
                except TraitError, e:
                    self.debug(e)

        if hasattr(record, 'cdd_ic_factor'):
            ic = record.cdd_ic_factor
            if ic is None:
                self.debug('Using default CDD IC factor 1.0')
                ic = ufloat(1, 1.0e-20)

            self.ic_factor_v = float(ic.nominal_value)
            self.ic_factor_e = float(ic.std_dev)
        else:
            self.debug('{} has no ic_factor attribute'.format(record, ))

    def open_file(self):
        return self.data_manager.open_file(self.data_path)

    def iter_isotopes(self):
        def _iter():
            dm = self.data_manager
            #with dm.open_file(self.data_path):
            hfile = dm._frame
            root = dm._frame.root
            signal = root.signal
            for isogroup in hfile.listNodes(signal):
                for dettable in hfile.listNodes(isogroup):
                    iso = isogroup._v_name
                    det = dettable.name
                    self.debug('{} {}'.format(iso, det))
                    yield iso, det

        return _iter()

    def get_blank_uvalue(self, iso):
        try:
            b = self.blanks[iso]
        except KeyError:
            self.debug('no blank for {} {}'.format(iso, self.blanks.keys()))
            b = ufloat(0, 0)

        return b

    def get_signal_uvalue(self, iso, det):
        #if iso in self._processed_signals_dict:
        try:
            ps = self.signal_intercepts['{}signal'.format(iso)]
        except KeyError, e:
            self.debug('no key {} {}'.format(iso,
                                             self.signal_intercepts.keys()))
            ps = ufloat(0, 0)

        return ps

    def get_signal_fit(self, iso, det):
        #f=next((si for si,di in self.signal_fits
        #        if di.name==det),None)
        try:
            f = self.signal_fits[det]
        except KeyError:
            f = 'linear'
        return f

    def get_baseline_fit(self, det):
        return 'average_SEM'

    def get_baseline_data(self, iso, det):
        return self._get_data('baseline', iso, det)

    def get_signal_data(self, iso, det):
        return self._get_data('signal', iso, det)

    def get_baseline_uvalue(self, det):
        vb = []

        dm = self.data_manager
        #with dm.open_file(self.data_path):
        hfile = dm._frame
        root = dm._frame.root
        baseline = root.baseline
        for isogroup in hfile.listNodes(baseline):
            for dettable in hfile.listNodes(isogroup):
                if dettable.name == det:
                    vb = [r['value'] for r in dettable.iterrows()]
                    break
        vb = array(vb)
        v = vb.mean()
        e = vb.std()

        return ufloat(v, e)


    def _get_data(self, group, iso, det):
        dm = self.data_manager
        #with dm.open_file(self.data_path):
        root = dm._frame.root

        group = getattr(root, group)
        try:
            isog = getattr(group, iso)
            tab = getattr(isog, det)
            data = [(row['time'], row['value'])
                    for row in tab.iterrows()]
            t, v = zip(*data)
        except AttributeError:
            t, v = [0, ], [0, ]

        return t, v

        #def iter(self):
    #    for a in ('detectors', 'signals', 'baselines', 'blanks', 'signal_intercepts', 'baseline_intercepts',
    #              'signal_fits', 'baseline_fits'):
    #        v = getattr(self, a)
    #        self.debug('attr={} n={} {}'.format(a, len(v), v))
    #
    #    ##dont use zip
    #    #return zip(self.detectors,
    #    #           self.signals,
    #    #           self.baselines,
    #    #           self.blanks,
    #    #           self.signal_intercepts,
    #    #           self.baseline_intercepts,
    #    #           self.signal_fits,
    #    #           self.baseline_fits)
    #    def _iter():
    #        self.debug('detectors----- {}'.format(self.detectors))
    #        for i, detector in enumerate(self.detectors):
    #            signal = self.signals[i]
    #            baseline = self._get_list_attr('baselines', i)
    #            #baseline = self.baselines[i]
    #            blank = self.blanks[i]
    #            sintercept = self.signal_intercepts[i]
    #            bsintercept = self.baseline_intercepts[i]
    #            sfits = self.signal_fits[i]
    #            #bfits = self.baseline_fits[i]
    #            bfits = self._get_list_attr('baseline_fits', i, default='average_SEM')
    #            #self.debug('{} detector {}'.format(i, detector))
    #            #self.debug('{} signal {}'.format(i, signal))
    #            #self.debug('{} baseline {}'.format(i, baseline))
    #            #self.debug('{} blank {}'.format(i, blank))
    #            #self.debug('{} sint {}'.format(i, sintercept))
    #            #self.debug('{} bint {}'.format(i, bsintercept))
    #            #self.debug('{} sfit {}'.format(i, sfits))
    #            #self.debug('{} bfit {}'.format(i, bfits))
    #            yield detector, signal, baseline, blank, sintercept, bsintercept, sfits, bfits
    #
    #    return _iter()

    #def _get_list_attr(self, attr, idx, default=None):
    #    try:
    #        return getattr(self, attr)[idx]
    #    except IndexError:
    #        if default is None:
    #            default = [(0, 0)]
    #        return default

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
