'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
from traits.api import HasTraits, Bool, Float, Button, Instance, Range, Any, Str, Property
from traitsui.api import View, Item, Group, HGroup, RangeEditor, spring
from chaco.api import AbstractOverlay

#============= standard library imports ========================
from numpy import array, transpose, flipud
#============= local library imports  ==========================
from pattern_generators import square_spiral_pattern, line_spiral_pattern, random_pattern, \
    polygon_pattern, arc_pattern

from src.graph.graph import Graph
import os
from src.image.image import Image
from chaco.data_range_1d import DataRange1D
from chaco.linear_mapper import LinearMapper

class TargetOverlay(AbstractOverlay):
    target_radius = Float
    cx = Float
    cy = Float
    def overlay(self, component, gc, *args, **kw):
        gc.save_state()
        x, y = self.component.map_screen([(self.cx, self.cy)])[0]
        pts = self.component.map_screen([(0, 0), (self.target_radius, 0)])
        r = abs(pts[0][0] - pts[1][0])

        gc.begin_path()
        gc.arc(x + 1 , y + 1 , r, 0, 360)
        gc.stroke_path()

        gc.restore_state()

class OverlapOverlay(AbstractOverlay):
    beam_radius = Float(1)
    def overlay(self, component, gc, *args, **kw):
        gc.save_state()
        gc.clip_to_rect(component.x,
                component.y,
                        component.width, component.height)

        xs = component.index.get_data()
        ys = component.value.get_data()
        gc.set_stroke_color((0, 0, 0, 0))

        pts = component.map_screen([(0, 0), (self.beam_radius, 0)])
        rad = abs(pts[0][0] - pts[1][0])
        i = 0
        for xi, yi in component.map_screen(zip(xs, ys)):
#            gc.set_alpha(0.5)
            gc.set_fill_color((0, 0, 1, 1.0 / (0.75 * i + 1) * 0.5))
            gc.begin_path()
            gc.arc(xi, yi, rad, 0, 360)
            gc.draw_path()
            i += 1


        gc.restore_state()


class Pattern(HasTraits):

    graph = Instance(Graph, (), transient=True)
    cx = Float(transient=True)
    cy = Float(transient=True)
    target_radius = Float(1)

#    beam_radius = Float(1, enter_set=True, auto_set=False)
    show_overlap = Bool(False)
    beam_radius = Range(0.0, 3.0, 1)

    path = Str
    name = Property(depends_on='path')

    image_width = 640
    image_height = 480
    xbounds = (-2, 2)
    ybounds = (-2, 2)
    pxpermm = None
    def map_pt(self, x, y):

        return self.pxpermm * x + self.image_width / 2, self.pxpermm * y + self.image_height / 2

    def _get_name(self):
        if not self.path:
            return 'Pattern'
        return os.path.basename(self.path).split('.')[0]
#    graph_width = 200
#    graph_height = 200

    def _anytrait_changed(self, name, new):
        self.replot()

    def _beam_radius_changed(self):
        oo = self.graph.plots[0].plots['plot0'][0].overlays[1]
        oo.beam_radius = self.beam_radius
        self.replot()

    def _show_overlap_changed(self):
        oo = self.graph.plots[0].plots['plot0'][0].overlays[1]
        oo.visible = self.show_overlap
        oo.request_redraw()

    def set_mapping(self, px):
        self.pxpermm = px / 10.0


    def set_image(self, data, graph=None):
        '''
            px,py pixels per cm x and y
        '''
        if graph is None:
            graph = self.graph

#        p = graph.plots[0].plots['plot0'][0]
#        for ui in p.underlays:
#            if isinstance(ui, ImageUnderlay):
#                ui.image.load(img)
#                break
#        else:
        if isinstance(data, str):
            image = Image()
            image.load(data)
            data = image.get_array()
        else:
            data = data.as_numpy_array()
            data = data.copy()
            data = flipud(data)

#            mmx = px / 10.0 * (self.xbounds[1] - self.xbounds[0])
#            mmy = py / 10.0 * (self.ybounds[1] - self.ybounds[0])
#
#            w = 640
#            h = 480
#            cb = [w / 2 - mmx, w / 2 + mmx, h / 2 - mmy, h / 2 + mmy]
#            cb = [h / 2 - mmy, h / 2 + mmy, w / 2 - mmx, w / 2 + mmx ]

        graph.plots[0].data.set_data('imagedata', data)
        graph.plots[0].img_plot('imagedata')

#            io = ImageUnderlay(component=p, image=image, crop_rect=(640 / 2, 480 / 2, mmx, mmy))
#
#            p.underlays.append(io)

        graph.redraw()

    def pattern_generator_factory(self, **kw):
        raise  NotImplementedError

    def replot(self):
        self.plot()

    def plot(self):
        pgen_out = self.pattern_generator_factory()
        data_out = array([pt for pt in pgen_out])
        xs, ys = transpose(data_out)

        if self.pxpermm is not None:
            xs, ys = self.map_pt(xs, ys)

        self.graph.set_data(xs)
        self.graph.set_data(ys, axis=1)

        return data_out[-1][0], data_out[-1][1]

    def points_factory(self):
        gen_out = self.pattern_generator_factory()
        return [pt for pt in gen_out]

    def graph_view(self):
        v = View(Item('graph', style='custom', show_label=False,
                      width=350,
                      height=350
                      ),
                 #title=self.name
                 )
        return v

    def _get_crop_bounds(self):
        px = self.pxpermm
#        mmx = px / 10.0 * 1 / (self.xbounds[1] - self.xbounds[0])
#        mmy = py / 10.0 * 1 / (self.ybounds[1] - self.ybounds[0])
        windx = (self.xbounds[1] - self.xbounds[0])
        mmx = windx * px / 2

        windy = (self.ybounds[1] - self.ybounds[0])
        mmy = windy * px / 2

        w = self.image_width
        h = self.image_height

        cbx = [w / 2 - mmx, w / 2 + mmx ]
        cby = [h / 2 - mmy, h / 2 + mmy]

        return cbx, cby

    def reset_graph(self, **kw):
        self.graph = self._graph_factory(**kw)
#        pass
    def _graph_factory(self, with_image=False):
        g = Graph(

                  container_dict=dict(
                                        padding=0
                                        ))
        g.new_plot(
                   bounds=[250, 250],
                   resizable='',
                   padding=[30, 0, 0, 30])

        cx = self.cx
        cy = self.cy
        cbx = self.xbounds
        cby = self.ybounds
        tr = self.target_radius

        if with_image:
            px = self.pxpermm  #px is in mm
            cbx, cby = self._get_crop_bounds()
            #g.set_axis_traits(tick_label_formatter=lambda x: '{:0.2f}'.format((x - w / 2) / px))
            #g.set_axis_traits(tick_label_formatter=lambda x: '{:0.2f}'.format((x - h / 2) / px), axis='y')

            bx, by = g.plots[0].bounds
            g.plots[0].x_axis.mapper = LinearMapper(high_pos=bx,
                                                    range=DataRange1D(low_setting=self.xbounds[0],
                                                                      high_setting=self.xbounds[1]))
            g.plots[0].y_axis.mapper = LinearMapper(high_pos=by,
                                                    range=DataRange1D(low_setting=self.ybounds[0],
                                                                      high_setting=self.ybounds[1]))
            cx += self.image_width / 2
            cy += self.image_height / 2
            tr *= px

        g.set_x_limits(*cbx)
        g.set_y_limits(*cby)

        lp, _plot = g.new_series()
        lp.overlays.append(TargetOverlay(component=lp,
                                                      cx=cx,
                                                      cy=cy,
                                                      target_radius=tr
                                                      ))
        overlap_overlay = OverlapOverlay(component=lp,
                                              visible=self.show_overlap
                                              )
        lp.overlays.append(overlap_overlay)
        g.new_series(type='scatter', marker='circle')
        return g

    def _graph_default(self):
        return self._graph_factory()




#        p = '/Users/ross/Desktop/foo2.tiff'
#
#        i = Image()#width=640, height=480)
#        i.load(p)
#
#        self.set_image(i, px, px, graph=g)
#        from chaco.image_data import ImageData
#        image = ImageData.fromfile(p)
##        print image._data


#        crop(i.source_frame, 0, 0, 300, 300)
        #self.pattern.graph.plots[0].plots['plot0'][0].overlays.append(ImageUnderlay(image=i))
        #self.pattern.graph.plots[0].plots[0].underlays.append(ImageUnderlay(image=i))
#        io = ImageUnderlay(component=lp, image=i, visible=False)
#        lp.overlays.append(io)
    def maker_group(self):
        return Group(
                     self.get_parameter_group(),
                     Item('show_overlap'),
                     Item('beam_radius', enabled_when='show_overlap'),
                     Item('graph',
    #                      resizable=False,
                          show_label=False, style='custom'),
                       show_border=True,
                       label='Pattern'
                       )
    def maker_view(self):
        v = View(self.maker_group(),
                 buttons=['OK', 'Cancel'],
                 resizable=True
                 )
        return v

    def traits_view(self):
        v = View(self.maker_group(),
                 buttons=['OK', 'Cancel'],
                 title=self.name,
                 resizable=True
                 )
        return v

    def get_parameter_group(self):
        raise NotImplementedError


#class DiamondPattern(Pattern):
#    width = Float(1)
#    height = Float(1)
#    def get_parameter_group(self):
#        return Group('width',
#                     'height'
#                     )
#    def pattern_generator_factory(self, **kw):
#        return diamond_pattern(self.cx, self.cy, self.width, self.height, **kw)


class RandomPattern(Pattern):
    walk_x = Float(1)
    walk_y = Float(1)
    npoints = Range(0, 50, 10)
    regenerate = Button
    def _regenerate_fired(self):
        self.plot()

    def get_parameter_group(self):
        return Group('walk_x',
                     'walk_y',
                     'npoints',
                     HGroup(spring, Item('regenerate', show_label=False))
                     )

    def pattern_generator_factory(self, **kw):
        return random_pattern(self.cx, self.cy, self.walk_x, self.walk_y, self.npoints, **kw)

    def points_factory(self):
        gen_out = self.pattern_generator_factory()
        return [pt for pt in gen_out]


class PolygonPattern(Pattern):
    nsides = Range(3, 12)
    radius = Range(0.0, 1.0, 0.5)
    rotation = Range(0.0, 360.0, 0.0)

    def get_parameter_group(self):
        return Group(Item('radius'),
                     Item('nsides'),
                     Item('rotation', editor=RangeEditor(mode='slider',
                                                         low=0,
                                                         high=360
                                                         ))
                     )
    def pattern_generator_factory(self, **kw):
        return polygon_pattern(self.cx, self.cy, self.radius, self.nsides, rotation=self.rotation)

class ArcPattern(Pattern):
    radius = Range(0.0, 1.0, 0.5)
    degrees = Range(0.0, 360.0, 90)

    def get_parameter_group(self):
        return Group('radius',
                     Item('degrees', editor=RangeEditor(mode='slider',
                                                        low=0,
                                                        high=360
                                                        ))
                     )
    def pattern_generator_factory(self, **kw):
        return arc_pattern(self.cx, self.cy, self.degrees, self.radius)

class SpiralPattern(Pattern):

    nsteps = Range(1, 10, 2)
    radius = Range(0.01, 0.5, 0.1)
    percent_change = Range(0.01, 5.0, 0.8)
    def replot(self):
        ox, oy = self.plot()
        self.plot_in(ox, oy)

    def points_factory(self):
        gen_out = self.pattern_generator_factory()
        gen_in = self.pattern_generator_factory(direction='in')
        return [pt for pt in gen_out] + [pt for pt in gen_in]

    def plot_in(self, ox, oy):
        pgen_in = self.pattern_generator_factory(ox=ox, #data_out[-1][0],
                                                 oy=oy, #data_out[-1][1],
                                                 direction='in')
        data_in = array([pt for pt in pgen_in])

        xs, ys = transpose(data_in)
#        self.graph.set_data(xs, series=1)
#        self.graph.set_data(ys, axis=1, series=1)

    def get_parameter_group(self):
        return Group('radius',
                     'nsteps',
                     'percent_change',
                     )

class LineSpiralPattern(SpiralPattern):
    step_scalar = Range(0, 20, 5)
    def get_parameter_group(self):
        g = super(LineSpiralPattern, self).get_parameter_group()
        g.content.append(Item('step_scalar'))
        return g

    def pattern_generator_factory(self, **kw):
        return line_spiral_pattern(self.cx, self.cy, self.radius,
                                      self.nsteps,
                                      self.percent_change,
                                      self.step_scalar,
                                      **kw
                                      )

class SquareSpiralPattern(SpiralPattern):
    def pattern_generator_factory(self, **kw):
        return square_spiral_pattern(self.cx, self.cy, self.radius,
                                      self.nsteps,
                                      self.percent_change,
                                      **kw
                                      )



if __name__ == '__main__':
    p = PolygonPattern()
    p.configure_traits()
#============= EOF ====================================
