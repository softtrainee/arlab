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
from traits.api import HasTraits, List, Property, Str, Enum, Int
from traitsui.api import View, Item, HGroup, Label, Group, \
    TableEditor, ListEditor, InstanceEditor, EnumEditor, Spring, spring, VGroup
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
    height = Int(100)
    def _get_plot_names(self):
        return {NULL_STR:NULL_STR,
                'analysis_number':'Analysis Number',
                'radiogenic':'Radiogenic 40Ar',
                'kca':'K/Ca'
                }
    def traits_view(self):
        v = View(
                 HGroup(
                        Item('name',
                             show_label=False,
                             editor=EnumEditor(name='plot_names')),

                        Item('scale', show_label=False),
                        Item('height')
                        ),
                )

        return v


FONTS = ['Helvetica', 'Courier', 'Modern']
SIZES = [6, 8, 9, 10, 11, 12, 14, 16, 18, 24, 36]


class PlotterOptions(Viewable):
    title = Str
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


    def __init__(self, clean=False, *args, **kw):
        super(PlotterOptions, self).__init__(*args, **kw)
        if not clean:
            self._load()

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
    def dump(self):
        self._dump()

    def _dump(self):
        if not self.name:
            return
        p = os.path.join(paths.plotter_options_dir, self.name)
        with open(p, 'w') as fp:
            d = dict()
            attrs = ['title', 'aux_plots',
                     'xtick_font_size',
                     'xtick_font_name',
                     'xtitle_font_size',
                     'xtitle_font_name',
                     'ytick_font_size',
                     'ytick_font_name',
                     'ytitle_font_size',
                     'ytitle_font_name',
                     ]
            for t in attrs:
                d[t] = getattr(self, t)

            pickle.dump(d, fp)

    def _load(self):
        p = os.path.join(paths.plotter_options_dir, self.name)
        if os.path.isfile(p):
            with open(p, 'r') as fp:
                try:
                    obj = pickle.load(fp)
                    self.trait_set(**obj)

                except (pickle.PickleError, TypeError):
                    pass


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
        return [PlotterOption() for i in range(5)]

#===============================================================================
# views
#===============================================================================
    def traits_view(self):
        v = View(Item('name'),
                 Item('title'),
                 VGroup(
                        self._create_axis_group('x', 'title'),
                        self._create_axis_group('x', 'tick'),
                        show_border=True,
                        label='X'),

                 VGroup(
                        self._create_axis_group('y', 'title'),
                        self._create_axis_group('y', 'tick'),
                        show_border=True,
                        label='Y'),

                 Item('aux_plots',
                      style='custom',
                      show_label=False,
                      editor=ListEditor(mutable=False,
                                        style='custom',
                                        editor=InstanceEditor())),
                 resizable=True,
#                 title='Plotter Options',
                 buttons=['OK', 'Cancel'],
                 handler=self.handler_klass
                 )
        return v


    def __repr__(self):
        return self.name
#============= EOF =============================================
