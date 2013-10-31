#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits, Str, Bool, Property, on_trait_change, \
    List, Event, Button
from traitsui.api import View, HGroup, UItem, EnumEditor, spring, Item
from traitsui.table_column import ObjectColumn
from traitsui.extras.checkbox_column import CheckboxColumn

from src.pychron_constants import FIT_TYPES, FIT_TYPES_INTERPOLATE
from src.ui.table_editor import myTableEditor

#============= standard library imports ========================
#============= local library imports  ==========================
class Fit(HasTraits):
    name = Str
    use = Bool
    show = Bool
    fit_types = Property
    #     fit = Enum(FIT_TYPES)
    fit = Str
    valid = Property(depends_on=('fit, use, show'))

    def _fit_default(self):
        return self.fit_types[0]

    def _get_fit_types(self):
        return FIT_TYPES

    def _get_valid(self):
        return self.use and self.show and self.fit

    def _show_changed(self):
        self.use = self.show

    def traits_view(self):
        v = View(HGroup(
            UItem('name', style='readonly'),
            UItem('show'),
            UItem('fit',
                  editor=EnumEditor(name='fit_types'),
                  enabled_when='show',
                  width=-50,
            ),
            UItem('use'),
        )
        )
        return v


class FitSelector(HasTraits):
    fits = List(Fit)
    update_needed = Event
    suppress_refresh_unknowns = Bool

    fit_klass = Fit
    command_key = Bool
    auto_update = Bool(True)

    def traits_view(self):
        v = View(self._get_fit_group())
        return v

    def _get_columns(self):
        cols = [ObjectColumn(name='name', editable=False),
                CheckboxColumn(name='show'),
                ObjectColumn(name='fit',
                             editor=EnumEditor(name='fit_types'),
                             width=75),
                CheckboxColumn(name='use', label='Save DB')]

        return cols

    def _get_fit_group(self):
        cols = self._get_columns()
        editor = myTableEditor(columns=cols,
                               sortable=False,
                               on_command_key=self._update_command_key)
        grp = UItem('fits',
                    style='custom',
                    editor=editor)
        return grp

    @on_trait_change('fits:[show, fit, use]')
    def _fit_changed(self, obj, name, old, new):
        if self.command_key:
            for fi in self.fits:
                fi.trait_set(trait_change_notify=False,
                             **{name: new})

        if self.auto_update:
            if name in ('show', 'fit'):
                self.update_needed = True

    def load_fits(self, keys, fits):

        nfs = []
        for ki, fi in zip(keys, fits):
            pf = next((fa for fa in self.fits if fa.name == ki), None)
            if pf is None:
                pf = self.fit_klass(name=ki, fit=fi)
            else:
                pf.fit = fi
            nfs.append(pf)

        self.fits = nfs

    #         self.fits = [
    #                      self.fit_klass(name=ki, fit=fi)
    #                      for ki, fi in zip(ks, fs)
    #                     ]

    def load_baseline_fits(self, keys):
        fits = self.fits
        if not fits:
            fits = []

        fs = [
            self.fit_klass(name='{}bs'.format(ki), fit='average_sem')
            for ki in keys
        ]

        fits.extend(fs)
        self.fits = fits

    def add_peak_center_fit(self):
        fits = self.fits
        if not fits:
            fits = []

        fs = self.fit_klass(name='PC', fit='average_sem')

        fits.append(fs)
        self.fits = fits

    def add_derivated_fits(self, keys):
        fits = self.fits
        if not fits:
            fits = []

        fs = [
            self.fit_klass(name='{}E'.format(ki), fit='average_sem')
            for ki in keys
        ]

        fits.extend(fs)
        self.fits = fits

    def _update_command_key(self, new):
        self.command_key = new


class InterpolationFit(Fit):
    def _get_fit_types(self):
        return FIT_TYPES_INTERPOLATE


class InterpolationFitSelector(FitSelector):
    fit_klass = InterpolationFit


class IsoEvoFitSelector(FitSelector):
    plot_button = Button('Plot')

    def load_fits(self, keys, fits):
        bs = [
            '{}bs'.format(ki) for ki in keys
        ]
        bfs = ['average_SEM' for fi in fits]
        #         for ki in keys:
        super(IsoEvoFitSelector, self).load_fits(keys + bs, fits + bfs)

    def _plot_button_fired(self):
        self.update_needed = True

    def _auto_update_changed(self):
        self.update_needed = True

    def traits_view(self):
        v = View(
            HGroup(UItem('plot_button',
                         tooltip='Replot the isotope evolutions. \
This may take awhile if many analyses are selected'),
                   spring,
                   Item('auto_update',
                        label='Auto Plot',
                        tooltip='Should the plot refresh after each change ie. "fit" or "show". \
It is not advisable to use this option with many analyses')),
            self._get_fit_group())
        return v

#============= EOF =============================================
