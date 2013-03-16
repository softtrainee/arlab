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
from traits.api import HasTraits, Color, Button, Event, Property, \
    Any, List, Bool, Enum, Float, Int, Instance, cached_property, Str
from traitsui.api import View, Item, ButtonEditor, Group, HGroup, VGroup
#============= standard library imports ========================
import yaml
import os
from numpy import array,hstack
#============= local library imports  ==========================
from src.paths import paths
from src.managers.manager import Manager
from src.lasers.points.maker import BaseMaker, LineMaker, PointMaker, \
    PolygonMaker, TransectMaker
maker_dict = dict(polygon=PolygonMaker, point=PointMaker, line=LineMaker, transect=TransectMaker)

class PointsProgrammer(Manager):

    maker = Property(Instance(BaseMaker), depends_on='mode')

#===============================================================================
#
#===============================================================================

    stage_manager = Any
    canvas = Any
    program_points = Event
    show_hide = Event
    is_programming = Bool
    is_visible = Bool

    program_points_label = Property(depends_on='is_programming')
    show_hide_label = Property(depends_on='is_visible')

    load_points = Button
    save_points = Button

    stage_map_klass = Any
    mode = Enum('polygon', 'point', 'line', 'transect')

    point_entry = Property(Int(enter_set=True, auto_set=False))
    point = Any
    line_entry = Property(Int(enter_set=True, auto_set=False))
    line = Any
    polygon_entry = Property(Int(enter_set=True, auto_set=False))
    _polygon_entry = Int
    polygon = Any
    scan_size = Int(50)
    plot_scan = Button('Plot')
    use_move = Bool(False)

    @cached_property
    def _get_maker(self):
        if self.mode in maker_dict:
            maker = maker_dict[self.mode](canvas=self.canvas,
                                          stage_manager=self.stage_manager,
                                          )
            return maker

#    def _set_line_entry(self, v):
#        pts = self.canvas.lines
#        self.point = None
#        pp = next((pi for pi in pts if pi.identifier == str(v)), None)
#        if pp is not None:
#            self.line = pp
#        else:
#            self.line = None

    def _set_polygon_entry(self, v):
        if self.use_move:
            self._set_entry('polygon', v, ['point', 'line'])
        else:
            self._polygon_entry = v

    def _set_line_entry(self, v):
        self._set_entry('line', v, ['point', 'polygon'])

    def _set_point_entry(self, v):
        self._set_entry('point', v, ['line', 'polygon'])

    def _get_line_entry(self):
        return self._get_entry_identifer('line')

    def _get_point_entry(self):
        return self._get_entry_identifer('point')

    def _get_polygon_entry(self):
        return self._get_entry_identifer('polygon')

    def _set_entry(self, name, value, onames):
        for oi in onames:
            setattr(self, oi, None)

        objs = getattr(self.canvas, '{}s'.format(name))
        pp = next((pi for pi in objs if pi.identifier == str(value)), None)
        setattr(self, name, pp)

    def _get_entry_identifer(self, name):
        p = self._polygon_entry
        obj = getattr(self, name)
        if obj:
            p = obj.identifier

        return p

#===============================================================================
# handlers
#===============================================================================
    def _plot_scan_fired(self):
        polygons = self.canvas.polygons
        if self.polygon_entry is not None and self.scan_size:
            pp = next((pi for pi in polygons if pi.identifier == str(self.polygon_entry)), None)
            scan_size = None
            if hasattr(self.maker, 'scan_size'):
                scan_size = self.maker.scan_size
            else:
                scan_size=pp.scan_size
            
            poly=[(pi.x*1000, pi.y*1000) for pi in pp.points]

            from src.geometry.polygon_offset import polygon_offset
            from src.geometry.scan_line import make_raster_polygon
            use_offset=True
            if use_offset:
                opoly=polygon_offset(poly, -10)
                opoly=array(opoly, dtype=int)
                opoly=opoly[:,(0,1)]

#            print opoly, scan_size
            lines=make_raster_polygon(opoly, skip=scan_size)
            from src.graph.graph import Graph
    
            g=Graph()
            g.new_plot()
            
            for po in (poly, opoly): 
                po=array(po, dtype=int)
                try:
                    xs,ys=po.T
                except ValueError:
                    xs,ys,_=po.T
                xs=hstack((xs, xs[0]))                
                ys=hstack((ys, ys[0]))                
                g.new_series(xs,ys)
        
            for p1,p2 in lines:
                xi,yi=(p1[0], p2[0]), (p1[1], p2[1])
                g.new_series(xi, yi, color='green')
                
            g.edit_traits()

    def _show_hide_fired(self):
        canvas = self.canvas
        if self.is_visible:
            canvas.remove_markup_overlay()
        else:
            canvas.add_markup_overlay()

        canvas.request_redraw()
        self.is_visible = not self.is_visible

    def _program_points_fired(self):
        if self.is_programming:
            self.canvas.remove_markup_overlay()
            self.is_programming = False
            self.is_visible = False
        else:
            self.canvas.add_markup_overlay()
            self.is_programming = True
            self.is_visible = True

        self.canvas.request_redraw()

    def load_stage_map(self, sm):
        if not (hasattr(sm, 'lines') and hasattr(sm, 'points') and hasattr(sm, 'polygons')):
            return

        canvas = self.canvas

        canvas.clear_all()
        canvas.remove_markup_overlay()
        canvas.add_markup_overlay()

        ptargs = dict(radius=0.05,
                      vline_length=0.1, hline_length=0.1)

        point_color = self.maker.point_color
        for li in sm.lines:
            canvas._new_line = True
            for si in li:
                mi = si['mask'] if si.has_key('mask') else 0
                ai = si['attenuator'] if si.has_key('attenuator') else 0
                canvas.new_line_point(xy=si['xy'],
                                      z=si['z'],
                                      mask=mi, attenuator=ai,
                                      point_color=point_color,
                                       line_color=point_color,
                                       velocity=si['velocity'],
                                       **ptargs)

        for pi in sm.points:
            mi = pi['mask'] if pi.has_key('mask') else 0
            ai = pi['attenuator'] if pi.has_key('attenuator') else 0
            canvas.new_point(xy=pi['xy'],
                             z=pi['z'],
                             mask=mi, attenuator=ai,
                             default_color=point_color,
                                    **ptargs)

        for k, po in sm.polygons.iteritems():
            canvas._new_polygon = True
            v = po['velocity']
            use_convex_hull = po['use_convex_hull']
            scan_size = po['scan_size']
            mi = po['mask'] if po.has_key('mask') else 0
            ai = po['attenuator'] if po.has_key('attenuator') else 0
            for pi in po['points']:
                canvas.new_polygon_point(xy=pi['xy'],
                                         z=pi['z'],
                                         velocity=v,
                                         identifier=str(int(k) + 1),
                                         point_color=point_color,
                                         mask=mi, attenuator=ai,
                                         scan_size=scan_size,
                                         use_convex_hull=use_convex_hull,
                                         **ptargs)

        self.is_visible = True
        canvas.invalidate_and_redraw()

    def _load_points_fired(self):
        p = self.open_file_dialog(default_directory=paths.user_points_dir)
        if p:
            sm = self.stage_map_klass(file_path=p)
            self.load_stage_map(sm)
            self.is_programming = True

    def _save_points_fired(self):
        p = self.save_file_dialog(default_directory=paths.user_points_dir)

        if p:
            if not p.endswith('.yaml'):
                p = '{}.yaml'.format(p)
            d = self.maker.save()
            with open(p, 'w') as f:
                f.write(yaml.dump(d, default_flow_style=False))

            self.stage_manager.add_stage_map(p)
            head, _tail = os.path.splitext(os.path.basename(p))
            self.stage_manager.set_stage_map(head)

    def _get_program_points_label(self):
        return 'End Program' if self.is_programming else 'Program Positions'

    def _get_show_hide_label(self):
        return 'Hide' if self.is_visible else 'Show'

    def _mode_default(self):
        return 'polygon'

    def _clear_mode_default(self):
        return 'all'

    def traits_view(self):
        v = View(VGroup(
                       Item('point_entry', label='Point'),
                       Item('line_entry', label='Line'),

                       HGroup(Item('polygon_entry', label='Polygon'),
                              Item('use_move',
                                   tooltip='If checked the polygon rasterization will execute.'),
                              Item('plot_scan',
                                   show_label=False,
                                   tooltip='Display a plot of the calculated scan lines'
                                   ),
                              ),

                       Item('mode')
                       ),
                HGroup(Item('show_hide', show_label=False,
                         editor=ButtonEditor(label_value='show_hide_label')
                         ),
                    Item('program_points', show_label=False,
                         editor=ButtonEditor(label_value='program_points_label')
                         )
                       ),
                Item('maker', style='custom',
                     enabled_when='is_programming',
                     show_label=False),
                HGroup(Item('load_points', show_label=False),
                       Item('save_points', show_label=False)),
#                                 HGroup(Item('clear'), Item('clear_mode'), show_labels=False),
#                                 Item('finish', show_label=False, enabled_when='mode=="line" and object.is_programming'),
#                                 enabled_when='object.is_programming'
#                                 ),
        #                     label='Points'
#                             )
#                      )
               )
        return v

#============= EOF =============================================
