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
from traits.api import HasTraits, List, Property, Str, Enum, Int, Float, Bool
from traitsui.api import View, Item, HGroup, Label, Group, \
    ListEditor, InstanceEditor, EnumEditor, Spring, spring, VGroup, UItem
import apptools.sweet_pickle as pickle
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.constants import NULL_STR
from src.paths import paths
from src.viewable import Viewable

class PlotterOption(HasTraits):
    name = Str(NULL_STR)
    plot_names = Property

    scale = Enum('linear', 'log')
    height = Int(100, enter_set=True, auto_set=False)
    x_error = Bool(False)
    y_error = Bool(False)
    def _get_plot_names(self):
        return {NULL_STR:NULL_STR,
                'analysis_number':'Analysis Number',
                'radiogenic':'Radiogenic 40Ar',
                'kca':'K/Ca',
                'moles_K39':'K39 Moles'
                }
    def traits_view(self):
        v = View(
                 HGroup(
                        UItem('name',
                              width=-70,
                              editor=EnumEditor(name='plot_names')),
                        UItem('scale'),
                        UItem('height',
                              width=-50,
                             ),
#                        spring,
                        UItem('x_error'),
                        UItem('y_error'),
                        spring,
                        ),
                )

        return v


FONTS = ['modern', ]
SIZES = [6, 8, 9, 10, 11, 12, 14, 16, 18, 24, 36]


class PlotterOptions(Viewable):
    title = Str
    auto_generate_title = Bool
    data_type = Str('database')
    aux_plots = List

    xtick_font = Property
    xtick_font_size = Enum(*SIZES)
    xtick_font_name = Enum(*FONTS)

    xtitle_font = Property
    xtitle_font_size = Enum(*SIZES)
    xtitle_font_name = Enum(*FONTS)

    ytick_font = Property
    ytick_font_size = Enum(*SIZES)
    ytick_font_name = Enum(*FONTS)

    ytitle_font = Property
    ytitle_font_size = Enum(*SIZES)
    ytitle_font_name = Enum(*FONTS)
    data_type_editable = Bool(True)

    def __init__(self, root, clean=False, *args, **kw):
        super(PlotterOptions, self).__init__(*args, **kw)
        if not clean:
            self._load(root)

#    def closed(self, isok):
#        self._dump()

#    def close(self, isok):
#        if isok:
#            self._dump()
#        return True

    def construct_plots(self, plist):
        '''
            plist is a list of dictionaries
        '''
        ps = [PlotterOption(**pi) for pi in plist]
        self.aux_plots = ps

    def add_aux_plot(self, **kw):
        ap = PlotterOption(**kw)
        self.aux_plots.append(ap)

    def get_aux_plots(self):
        return reversed([pi
                for pi in self.aux_plots if pi.name != NULL_STR])


    def _create_axis_group(self, axis, name):

        hg = HGroup(
                    Label(name.capitalize()),
                    spring,
                    Item('{}{}_font_name'.format(axis, name), show_label=False),
                    Item('{}{}_font_size'.format(axis, name), show_label=False),
                    Spring(width=125, springy=False)
                    )
        return hg
#===============================================================================
# persistence
#===============================================================================
    def dump(self, root):
        self._dump(root)

    def _dump(self, root):
        if not self.name:
            return
        p = os.path.join(root, self.name)
        with open(p, 'w') as fp:
            d = dict()
            attrs = self._get_dump_attrs()
            for t in attrs:
                d[t] = getattr(self, t)

            pickle.dump(d, fp)

    def _load(self, root):
        p = os.path.join(root, self.name)
        if os.path.isfile(p):
            with open(p, 'r') as fp:
                try:
                    obj = pickle.load(fp)
                    self.trait_set(**obj)

                except (pickle.PickleError, TypeError, EOFError):
                    pass

    def _get_dump_attrs(self):
        attrs = ['title', 'auto_generate_title',
                 'data_type',
                  'aux_plots',
                     'xtick_font_size',
                     'xtick_font_name',
                     'xtitle_font_size',
                     'xtitle_font_name',
                     'ytick_font_size',
                     'ytick_font_name',
                     'ytitle_font_size',
                     'ytitle_font_name',
                     ]
        return attrs
#===============================================================================
# property get/set
#===============================================================================
    def _get_xtick_font(self):
        return self._get_font('xtick', default_size=10)

    def _get_xtitle_font(self):
        return self._get_font('xtitle', default_size=12)

    def _get_ytick_font(self):
        return self._get_font('ytick', default_size=10)

    def _get_ytitle_font(self):
        return self._get_font('ytitle', default_size=12)

    def _get_font(self, name, default_size=10):
        xn = getattr(self, '{}_font_name'.format(name))
        xs = getattr(self, '{}_font_size'.format(name))
        if xn is None:
            xn = FONTS[0]
        if xs is None:
            xs = default_size
        return '{} {}'.format(xn, xs)
#===============================================================================
# defaults
#===============================================================================
    def _xtitle_font_size_default(self):
        return 12

    def _xtick_font_size_default(self):
        return 10

    def _ytitle_font_size_default(self):
        return 12

    def _ytick_font_size_default(self):
        return 10

    def _aux_plots_default(self):
        return [PlotterOption() for _ in range(5)]

#===============================================================================
# views
#===============================================================================
    def _get_groups(self):
        pass

    def _get_x_axis_group(self):
        v = VGroup(
                    self._create_axis_group('x', 'title'),
                    self._create_axis_group('x', 'tick'),
#                    show_border=True,
                    label='X')
        return v

    def traits_view(self):
        header_grp = HGroup(Label('Plot'),
                            Spring(width=132, springy=False),
                            Label('Scale'),
                            spring, Label('Height'),

                            Label('X Err.'), Label('Y Err.'),
                            spring,)
        default_grp = VGroup(
                             HGroup(Item('auto_generate_title', tooltip='Auto generate a title based on the analysis list'),
                                    Item('title', springy=True, enabled_when='not auto_generate_title',
                                         tooltip='User specified plot title')),
                             Item('data_type',
                                  editor=EnumEditor(values={'database':'0:Database',
                                                            'data_file':'1:Data File',
                                                            'manual_entry':'2:Manual Entry'}),
                                  defined_when='data_type_editable'),

                             Group(
                                    self._get_x_axis_group(),
                                    VGroup(
                                           self._create_axis_group('y', 'title'),
                                           self._create_axis_group('y', 'tick'),
#                                           show_border=True,
                                           label='Y'),
                                   layout='tabbed'
                                    ),
                             header_grp,
                             Item('aux_plots',
                                  style='custom',
                                  show_label=False,
                                  editor=ListEditor(mutable=False,
                                                    style='custom',
                                                    editor=InstanceEditor()))
                             )
        grps = self._get_groups()
        if grps:
            default_grp.label = 'Plot'
            g = Group(default_grp, layout='tabbed')
            g.content.append(grps)

        else:
            g = Group(default_grp)

        v = View(
                 g,
                 resizable=True,
#                 title='Plotter Options',
                 buttons=['OK', 'Cancel'],
                 handler=self.handler_klass
                 )
        return v

    def __repr__(self):
        return self.name

class AgeOptions(PlotterOptions):
    include_j_error = Bool(True)
    include_irradiation_error = Bool(True)
    include_decay_error = Bool(False)
    nsigma = Enum(1, 2, 3)
    def _get_dump_attrs(self):
        attrs = super(AgeOptions, self)._get_dump_attrs()
        attrs += ['include_j_error',
                  'include_irradiation_error',
                  'include_decay_error',
                  'nsigma'
                  ]
        return attrs

class IdeogramOptions(AgeOptions):
    probability_curve_kind = Enum('cumulative', 'kernel')
    mean_calculation_kind = Enum('weighted mean', 'kernel')
    error_calc_method = Enum('SEM, but if MSWD>1 use SEM * sqrt(MSWD)', 'SEM')
    xlow = Float
    xhigh = Float
    use_centered_range = Bool
    centered_range = Float(0.5)

    def _get_x_axis_group(self):
        vg = super(IdeogramOptions, self)._get_x_axis_group()

        limits_grp = HGroup(Item('xlow', label='Min.'),
                            Item('xhigh', label='Max.'),
                            enabled_when='not object.use_centered_range'
                            )
        centered_grp = HGroup(Item('use_centered_range', label='Center'),
                            Item('centered_range', show_label=False, enabled_when='object.use_centered_range')
                            )
        vg.content.append(limits_grp)
        vg.content.append(centered_grp)

        return vg

    def _get_groups(self):
        g = Group(
                  Item('probability_curve_kind',
                       width=-150,
                       label='Probability Curve Method'),
                  Item('mean_calculation_kind',
                       width=-150,
                       label='Mean Calculation Method'),
                  Item('error_calc_method',
                       width=-150,
                       label='Error Calculation Method'),
                  Item('nsigma', label='Age Error NSigma'),
                  Item('include_j_error'),
                  Item('include_irradiation_error'),
                  Item('include_decay_error'),
                  label='Calculations'
                  )
        return g

    def _get_dump_attrs(self):
        attrs = super(IdeogramOptions, self)._get_dump_attrs()
        return attrs + [
                        'probability_curve_kind',
                        'mean_calculation_kind',
                        'error_calc_method',
                        'xlow', 'xhigh',
                        'use_centered_range', 'centered_range'
                        ]

class SpectrumOptions(AgeOptions):
    step_nsigma = Int(2)
    def _get_dump_attrs(self):
        attrs = super(SpectrumOptions, self)._get_dump_attrs()
        return attrs + ['step_nsigma']

class InverseIsochronOptions(AgeOptions):
    pass

if __name__ == '__main__':
    ip = IdeogramOptions()
    ip.configure_traits()
#============= EOF =============================================
