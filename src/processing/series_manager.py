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
from traits.api import HasTraits, Str, List, Bool, Float, Property, Instance
from traitsui.api import View, Item, HGroup, Label, EnumEditor, \
    spring, Group
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import re
#============= local library imports  ==========================
from src.helpers.traitsui_shortcuts import listeditor
from src.constants import FIT_TYPES
import os
from src.paths import paths
from src.viewable import Viewable

class SeriesOptions(HasTraits):
    name = Str
    show = Bool
    fit = Str
    scalar = Float(1)

    key = Property
    _key = Str
    def traits_view(self):
        v = View(HGroup(Label(self.name),
                        spring,
                        Item('show', show_label=False),
                        Item('fit', editor=EnumEditor(values=FIT_TYPES),
                             show_label=False,
                             enabled_when='show'
                             ))
                        )
        return v

    def _fit_default(self):
        return FIT_TYPES[0]

    def _set_key(self, k):
        self._key = k

    def _get_key(self):
        if self._key:
            return self._key
        else:
            return self.name
class PeakCenterOption(HasTraits):
    show = Bool(False)
    def traits_view(self):
        v = View(Item('show'))
        return v

class SeriesManager(Viewable):
    analyses = List
    series = Property
    calculated_values = List(SeriesOptions)
    measured_values = List(SeriesOptions)
    baseline_values = List(SeriesOptions)
    blank_values = List(SeriesOptions)
    background_values = List(SeriesOptions)
    peak_center_option = Instance(PeakCenterOption, ())
    use_single_window = Bool(False)

#===============================================================================
# viewable
#===============================================================================
    def close(self, isok):
        if isok:
            self.dump()
        return True

    def opened(self):
        self.load()

#===============================================================================
# handlers
#===============================================================================
    def _analyses_changed(self):
        if self.analyses:
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

            self.calculated_values = [SeriesOptions(name=ki, key=ki.replace('Ar', 's')) for ki in keys]
            self.measured_values = [SeriesOptions(name=ki) for ki in keys]
            self.baseline_values = [SeriesOptions(name=ki, key='{}bs'.format(ki)) for ki in keys]
            self.blank_values = [SeriesOptions(name=ki, key='{}bl'.format(ki)) for ki in keys]
            self.background_values = [SeriesOptions(name=ki, key='{}bg'.format(ki)) for ki in keys]
            #make ratios
            for n, d in [('Ar40', 'Ar36')]:
                if n in keys and d in keys:
                    self.calculated_values.append(SeriesOptions(name='{}/{}'.format(n, d),
                                                     ))

            self.calculated_values.append(SeriesOptions(name='IC',
                                             key='Ar40/Ar36',
                                             scalar=295.5))

#===============================================================================
# persistence
#===============================================================================
    def dump(self):
        for ai in ['calculated_values', 'measured_values',
                    'baseline_values', 'blank_values', 'background_values']:
            self._dump(ai)

        p = os.path.join(paths.hidden_dir, 'series_manager.traits')
        with open(p, 'w') as fp:
            dd = dict([(ai, getattr(self, ai)) for ai in ['use_single_window']])
            pickle.dump(dd, fp)

    def _dump(self, attr):
        p = os.path.join(paths.hidden_dir, 'series_manager.{}'.format(attr))
        with open(p, 'w') as fp:
            pickle.dump(getattr(self, attr), fp)

    def load(self):
        for ai in ['calculated_values', 'measured_values',
                    'baseline_values', 'blank_values', 'background_values']:

            self._load(ai)

        p = os.path.join(paths.hidden_dir, 'series_manager.traits')
        if os.path.isfile(p):
            try:
                with open(p, 'r') as fp:
                    dd = pickle.load(fp)
                    self.trait_set(**dd)
            except pickle.PickleError:
                pass

    def _load(self, attr):
        p = os.path.join(paths.hidden_dir, 'series_manager.{}'.format(attr))
        if os.path.isfile(p):
            try:
                with open(p, 'r') as fp:
                    nso = pickle.load(fp)
                    for si in nso:
                        obj = next((ni for ni in getattr(self, attr)
                                    if ni.key == si.key and ni.name == si.name), None)
                        for ai in ['show', 'fit']:
                            setattr(obj, ai, getattr(si, ai))

            except pickle.PickleError:
                pass

#===============================================================================
# property get/set
#===============================================================================
#    def _get_series(self):
#        return self.calculated_values + self.measured_values + \
#                self.baseline_values + self.blank_values
#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        v = View(
                 Group(
                     Group(listeditor('calculated_values'), label='Calculated'),
                     Group(listeditor('measured_values'), label='Measured'),
                     Group(listeditor('baseline_values'), label='Baseline'),
                     Group(listeditor('blank_values'), label='Blanks'),
                     Group(listeditor('background_values'), label='Backgrounds'),
                     Group(Item('peak_center_option'), label='Peak Centers'),
                     layout='tabbed'
                     ),
                 buttons=['OK', 'Cancel'],
                 handler=self.handler_klass,
                 title='Select Series',
                 width=500

                 )
        return v
#============= EOF =============================================
