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
from traits.api import HasTraits, List, Str, Property, Event, Float, \
    Either, Int
from traitsui.api import View, UItem, TabularEditor, HGroup, Group

#============= standard library imports ========================
#============= local library imports  ==========================
from traitsui.tabular_adapter import TabularAdapter
from src.helpers.formatting import floatfmt, calc_percent_error
from src.ui.tabular_editor import myTabularEditor

SIGMA_1 = u'\u00b11\u03c3'
TABLE_FONT = 'arial 11'

vwidth = Int(60)
ewidth = Int(50)
pwidth = Int(40)


class BaseTabularAdapter(TabularAdapter):
    default_bg_color = '#F7F6D0'
    font = TABLE_FONT


class IsotopeTabularAdapter(BaseTabularAdapter):
    columns = [('Iso.', 'name'),
               ('Det.', 'detector'),
               ('Fit', 'fit_abbreviation'),
               ('Int.', 'value'),
               (SIGMA_1, 'error'),
               ('%', 'value_percent_error'),
               ('Base.', 'base_value'),
               (SIGMA_1, 'base_error'),
               ('%', 'baseline_percent_error'),
               ('Blank', 'blank_value'),
               (SIGMA_1, 'blank_error'),
               ('%', 'blank_percent_error'),
    ]

    value_text = Property
    error_text = Property
    base_value_text = Property
    base_error_text = Property
    blank_value_text = Property
    blank_error_text = Property

    value_percent_error_text = Property
    blank_percent_error_text = Property
    baseline_percent_error_text = Property

    name_width = Int(40)
    fit_width = Int(40)
    detector_width = Int(40)

    value_width = vwidth
    error_width = ewidth

    base_value_width = vwidth
    base_error_width = ewidth
    blank_value_width = vwidth
    blank_error_width = ewidth

    value_percent_error_width = pwidth
    blank_percent_error_width = pwidth
    baseline_percent_error_width = pwidth

    def _get_value_text(self, *args, **kw):
        v = self.item.get_corrected_value()
        return floatfmt(v.nominal_value)

    def _get_error_text(self, *args, **kw):
        v = self.item.get_corrected_value()
        return floatfmt(v.std_dev)

    def _get_base_value_text(self, *args, **kw):
        return floatfmt(self.item.baseline.value)

    def _get_base_error_text(self, *args, **kw):
        return floatfmt(self.item.baseline.error)

    def _get_blank_value_text(self, *args, **kw):
        return floatfmt(self.item.blank.value)

    def _get_blank_error_text(self, *args, **kw):
        return floatfmt(self.item.blank.error)

    def _get_baseline_percent_error_text(self, *args):
        b = self.item.baseline
        return calc_percent_error(b.value, b.error)

    def _get_blank_percent_error_text(self, *args):
        b = self.item.blank
        return calc_percent_error(b.value, b.error)

    def _get_value_percent_error_text(self, *args):
        cv = self.item.get_corrected_value()
        return calc_percent_error(cv.nominal_value, cv.std_dev)


class ComputedValueTabularAdapter(BaseTabularAdapter):
    columns = [('Name', 'name'),
               ('Value', 'value'),
               (SIGMA_1, 'error')]


class ExtractionTabularAdapter(BaseTabularAdapter):
    columns = [('Name', 'name'),
               ('Value', 'value'),
               ('Units', 'units')]


class MeasurementTabularAdapter(BaseTabularAdapter):
    columns = [('Name', 'name'),
               ('Value', 'value'), ]


class NamedValue(HasTraits):
    name = Str
    value = Either(Str, Float, Int)


class ComputedValue(NamedValue):
    error = Either(Str, Float, Int)


class ExtractionValue(NamedValue):
    units = Str


class MeasurementValue(NamedValue):
    pass


class AnalysisView(HasTraits):
    analysis_id = Str
    analysis_type = Str

    isotopes = List
    refresh_needed = Event

    computed_values = List
    extraction_values = List
    measurement_values = List

    def load(self, an):
        self.isotopes = [an.isotopes[k] for k in an.isotope_keys]

        self.load_computed(an)
        self.load_extraction(an)
        self.load_measurement(an)

    def _get_irradiation(self, an):
        return an.irradiation_str

    def _get_j(self, an):
        return an.j

    def load_measurement(self, an):
        j = self._get_j(an)
        ms = [
            MeasurementValue(name='AnalysisID',
                             value=self.analysis_id),
            MeasurementValue(name='Spectrometer',
                             value=an.mass_spectrometer),
            MeasurementValue(name='Run Date',
                             value=an.rundate.isoformat(' ')),
            MeasurementValue(name='Irradiation',
                             value=self._get_irradiation(an)),
            MeasurementValue(name='J',
                             value=u'{:0.4f} \u00b1{:0.2e}'.format(j.nominal_value, j.std_dev)
            ),
            MeasurementValue(name='Sample',
                             value=an.sample),
            MeasurementValue(name='Material',
                             value=an.material),
        ]
        self.measurement_values = ms

    def load_extraction(self, an):

        ev = [
            ExtractionValue(name='Device',
                            value=an.extract_device),
            ExtractionValue(name='Position',
                            value=an.position,
            ),
            ExtractionValue(name='Extract Value',
                            value=an.extract_value,
                            units=an.extract_units,
            ),
            ExtractionValue(name='Duration',
                            value=an.duration,
                            units='s'
            ),
            ExtractionValue(name='Cleanup',
                            value=an.cleanup,
                            units='s'
            ),
        ]

        self.extraction_values = ev

    def load_computed(self, an, newlist=True):
        attrs = None
        if self.analysis_type == 'unknown':
            attrs = (('Age', 'age'),
                     ('K/Ca', 'kca'),
                     ('K/Cl', 'kcl'),
                     ('40Ar*', 'rad40_percent'),
                     ('40Ar*/39ArK', 'R'),
            )
        elif self.analysis_type == 'cocktail':
            attrs = (('40Ar/39Ar', 'Ar40/Ar39'),)
        elif self.analysis_type == 'air':
            attrs = (('40Ar/36Ar', 'Ar40/Ar36'),
                     ('40Ar/38Ar', 'Ar40/Ar38'))

        if attrs:
            if newlist:
                cv = [ComputedValue(name=name,
                                    tag=attr,
                                    value=floatfmt(getattr(an, attr).nominal_value),
                                    error=floatfmt(getattr(an, attr).std_dev),
                )
                      for name, attr in attrs]

                if self.analysis_type == 'unknown':
                    #insert error w/o j
                    cv.insert(1, ComputedValue(name='w/o J',
                                               tag='wo_j',
                                               value='',
                                               error=an.age_error_wo_j
                    ))
                self.computed_values = cv
            else:
                for ci in self.computed_values:
                    attr = ci.tag
                    if attr == 'wo_j':
                        ci.error = an.age_error_wo_j
                    else:
                        ci.value = floatfmt(getattr(an, attr).nominal_value)
                        ci.error = floatfmt(getattr(an, attr).std_dev)

    def _get_editors(self):
        teditor = myTabularEditor(adapter=IsotopeTabularAdapter(),
                                  editable=False,
                                  refresh='refresh_needed')

        ceditor = myTabularEditor(adapter=ComputedValueTabularAdapter(),
                                  editable=False,
                                  refresh='refresh_needed')

        eeditor = myTabularEditor(adapter=ExtractionTabularAdapter(),
                                  editable=False,
        )
        meditor = myTabularEditor(adapter=MeasurementTabularAdapter(),
                                  editable=False)

        return teditor, ceditor, eeditor, meditor


    def traits_view(self):
        teditor, ceditor, eeditor, meditor = self._get_editors()

        v = View(
            HGroup(
                UItem('measurement_values',
                      editor=meditor),
                UItem('extraction_values',
                      editor=eeditor),
            ),
            UItem('isotopes',
                  editor=teditor),
            UItem('computed_values',
                  editor=ceditor
            )
        )
        return v


class DBAnalysisView(AnalysisView):
    pass


class AutomatedRunAnalysisView(AnalysisView):
    def update_values(self, arar_age):
        for ci in self.computed_values:
            v = getattr(arar_age, ci)

    def load(self, ar):
        an = ar.arar_age
        self.isotopes = [an.isotopes[k] for k in an.isotope_keys]
        #for iso in self.isotopes:
        #    print iso, iso.name, 'det', iso.detector

        self._irradiation_str = ar.spec.irradiation
        self._j = an.j

        self.load_computed(an)
        self.load_extraction(ar.spec)
        self.load_measurement(ar.spec)

    def _get_irradiation(self, an):
        return self._irradiation_str

    def _get_j(self, an):
        return self._j

    def traits_view(self):
        teditor, ceditor, eeditor, meditor = self._get_editors()

        isotopes = UItem('isotopes', editor=teditor, label='Isotopes')

        ratios = UItem('computed_values', editor=ceditor, label='Ratios')

        meas = UItem('measurement_values',
                     editor=meditor, label='General')

        extract = UItem('extraction_values',
                        editor=eeditor,
                        label='Extraction')

        v = View(
            Group(isotopes, ratios, extract, meas, layout='tabbed'),
        )
        return v

#============= EOF =============================================
