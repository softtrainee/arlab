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
from chaco.axis import DEFAULT_TICK_FORMATTER
from traits.api import HasTraits, Any, Float, Int, on_trait_change, Bool
from traitsui.api import View, Item, Group, VGroup
# from pyface.timer.do_later import do_later
# from traitsui.editors.range_editor import RangeEditor
# from numpy.core.numeric import Inf
# from src.ui.double_spinner import DoubleSpinnerEditor
#============= standard library imports ========================
#============= local library imports  ==========================
class EFloat(Float):
    enter_set = True
    auto_set = False


class EInt(Int):
    enter_set = True
    auto_set = False


class PlotEditor(HasTraits):
    xmin = EFloat
    xmax = EFloat
    ymin = EFloat
    ymax = EFloat
    xauto = Bool
    yauto = Bool

    plot = Any
    padding_left = EInt
    padding_right = EInt
    padding_top = EInt
    padding_bottom = EInt

    title_spacing = EFloat
    tick_visible = Bool
    x_grid = Bool
    y_grid = Bool

    @on_trait_change('padding+')
    def _update_padding(self, name, new):
        self.plot.trait_set(**{name: new})
        self.plot._layout_needed = True
        self.plot.invalidate_and_redraw()

    @on_trait_change('title_spacing')
    def _update_value_axis(self, name, new):
        self.plot.value_axis.title_spacing = new
        self.plot.invalidate_and_redraw()

    @on_trait_change('tick_visible')
    def _update_tick_visible(self, name, new):
        if new:
            fmt = DEFAULT_TICK_FORMATTER
        else:
            fmt = lambda x: ''
        self.plot.value_axis.tick_visible = new
        self.plot.value_axis.trait_set(**{'tick_visible': new,
                                          'tick_label_formatter': fmt
        })
        self.plot.invalidate_and_redraw()

        #

    @on_trait_change('x_grid, y_grid')
    def _update_grids(self, name, new):
        getattr(self.plot, name).visible = new

    def _plot_changed(self):
        self.xmin = self.plot.index_range.low
        self.xmax = self.plot.index_range.high

        self.ymin = self.plot.value_range.low
        self.ymax = self.plot.value_range.high

        for attr in ('left', 'right', 'top', 'bottom'):
            attr = 'padding_{}'.format(attr)
            setattr(self, attr, getattr(self.plot, attr))

        self.title_spacing = self.plot.value_axis.title_spacing
        self.tick_visible = self.plot.value_axis.tick_visible

        self.x_grid = self.plot.x_grid.visible
        self.y_grid = self.plot.y_grid.visible

    def _xmin_changed(self):
        p = self.plot
        v = p.index_range.high
        if self.xmin < v:
            p.index_range.low_setting = self.xmin
            self.xauto = False

        try:
            self.plot.index.metadata_changed = True
        except AttributeError:
            pass

    def _xmax_changed(self):
        p = self.plot
        v = p.index_range.low
        if self.xmax > v:
            p.index_range.high_setting = self.xmax
            self.xauto = False

        try:
            p.default_index.metadata_changed = True
        except AttributeError:
            pass

    def _ymin_changed(self):
        p = self.plot
        v = p.value_range.high
        if self.ymin < v:
            p.value_range.low_setting = self.ymin
            self.yauto = False

    def _ymax_changed(self):
        p = self.plot
        v = p.value_range.low
        if self.ymax > v:
            p.value_range.high_setting = self.ymax
            self.yauto = False

            #    def _xauto_changed(self):
            #        if self.xauto:
            #            p = self.plot
            #            p.index_range.low_setting = 'auto'
            #            p.index_range.high_setting = 'auto'
            #            p.index_range.refresh()
            #            p.invalidate_and_redraw()
            #            print p.index_range.high, p.index_range.low


    def traits_view(self):
        y_grp = Group(
            Item('title_spacing'),
            Item('tick_visible'),
            label='Y Axis',
        )

        grids_grp = Group(
            Item('x_grid'),
            Item('y_grid'),
            label='Grids'
        )

        v = View(
            VGroup(
                Group(
                    #                           Item('xauto', label='Autoscale'),
                    Item('xmin'),
                    Item('xmax'),
                ),
                Group(
                    #                           Item('yauto', label='Autoscale'),
                    Item('ymin'),
                    Item('ymax'),
                ),
                Group(
                    Item('padding_left', label='Left'),
                    Item('padding_right', label='Right'),
                    Item('padding_top', label='Top'),
                    Item('padding_bottom', label='Bottom'),
                    label='Padding'
                ),
                y_grp,
                grids_grp
            )
        )
        return v
        #============= EOF =============================================
