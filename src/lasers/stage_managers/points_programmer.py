from traits.api import HasTraits, Color, Button, Event, Property, \
    Any, List, Bool, Enum, Float, Int
from traitsui.api import View, Item, ButtonEditor, Group, HGroup, VGroup
from src.paths import paths
# from src.lasers.stage_managers.stage_map import StageMap
from src.loggable import Loggable
import yaml
from src.managers.manager import Manager
import os

'''
    add transect programming. define two end points, define step distance. 
    save each step as a point
'''
class PointsProgrammer(Manager):

    stage_manager = Any
    canvas = Any
    program_points = Event
    show_hide = Event
    is_programming = Bool
    is_visible = Bool
    finish = Button

    program_points_label = Property(depends_on='is_programming')
    show_hide_label = Property(depends_on='is_visible')

    load_points = Button
    save_points = Button
    clear = Button
    clear_mode = Enum('all', 'all lines', 'all points', 'current line',
                    'current point', 'last point'
                    )
    accept_point = Button
    stage_map_klass = Any
#    mode = Enum('transect', 'point', 'line')
    mode = Enum('polygon','point', 'line', 'transect')

    point_color = Color('green')

    use_convex_hull=Bool(True)
    trace_velocity = Float
    point_entry = Property(Int(enter_set=True, auto_set=False))
    point = Any
    line_entry = Property(Int(enter_set=True, auto_set=False))
    line = Any
    transect_step = Float(1, enter_set=True, auto_set=False)

    def _set_line_entry(self, v):
        pts = self.canvas.lines
        self.point=None
        pp = next((pi for pi in pts if pi.identifier == str(v)), None)
        if pp is not None:
            self.line = pp
        else:
            self.line=None

    def _get_line_entry(self):
        p = ''
        if self.line:
            p = self.line.identifier
        return p

    def _set_point_entry(self, v):
        self.line=None
        pts = self.canvas.points
        pp = next((pi for pi in pts if pi.identifier == str(v)), None)
        if pp is not None:
            self.point = pp
        else:
            self.point=None

    def _get_point_entry(self):
        p = ''
        if self.point:
            p = self.point.identifier
        return p
#===============================================================================
# handlers
#===============================================================================
    def _show_hide_fired(self):
        canvas = self.canvas
        if self.is_visible:
#            canvas.remove_point_overlay()
#            canvas.remove_line_overlay()
            canvas.remove_markup_overlay()
        else:
            canvas.add_markup_overlay()
#            canvas.add_point_overlay()
#            canvas.add_line_overlay()

        canvas.request_redraw()
        self.is_visible = not self.is_visible

    def _use_convex_hull_changed(self):
        poly=self.canvas.polygons[-1]
        poly.use_convex_hull=self.use_convex_hull
        self.canvas.request_redraw()
        
    def _transect_step_changed(self):
        if self.transect_step:
            self.canvas.set_transect_step(self.transect_step)

    def _clear_fired(self):
        cm = self.clear_mode
        if cm.startswith('current'):
            if cm == 'current line':
                self.canvas.lines.pop(-1)
            else:
                self.canvas.points.pop(-1)
        elif cm.startswith('all'):
            if cm == 'all':
                self.canvas.clear_all()
            elif cm == 'all lines':
                self.canvas.lines = []
            else:
                self.canvas.points = []
        else:
            line = self.canvas.lines[-1]
            if len(line.points):
                if self.mode == 'line':
                    line.points.pop(-1)
                    if line.lines:
                        line.lines.pop(-1)
                        line.velocity_segments.pop(-1)
                else:
                    self.canvas.points.pop(-1)

        self.canvas.request_redraw()

    def _program_points_fired(self):
        if self.is_programming:
            self.canvas.remove_markup_overlay()
            self.is_programming = False
            self.is_visible = False
#            self.canvas.remove_point_overlay()
#            self.canvas.remove_line_overlay()
        else:
            self.canvas.add_markup_overlay()
            self.is_programming = True
            self.is_visible = True

#            self.canvas.add_point_overlay()
#            self.canvas.add_line_overlay()

        self.canvas.request_redraw()
#        if not self.canvas.markup:
#            self.canvas.tool_state = 'point'
#        else:
#            self.canvas.tool_state = 'select'
#            if self.canvas.selected_element:
#                self.canvas.selected_element.set_state(False)
#                self.canvas.request_redraw()
#        self.canvas.markup = not self.canvas.markup
    def _finish_fired(self):
        self.canvas.reset_markup()
#        self.canvas._new_line = True
#        self.canvas._new_transect = True
#        self.canvas._new_polygon = True

    def _accept_point_fired(self):
        radius = 0.05  # mm or 50 um
        sm = self.stage_manager
        lm=sm.parent
        mask = lm.get_motor('mask')
        attenuator = lm.get_motor('attenuator')
        mask_value,attenuator_value=None, None
        if mask:
            radius = mask.get_discrete_value()
            if not radius:
                radius=0.05
            mask_value=mask.data_position
            
        if attenuator:
            attenuator_value=attenuator.data_position
            
        ptargs = dict(radius=radius, 
                      z=sm.get_z(),
                      mask=mask_value,
                      attenuator=attenuator_value,
                      vline_length=0.1, hline_length=0.1)

        if not self.canvas.point_exists():
            if self.mode == 'line':
                self.canvas.new_line_point(point_color=self.point_color,
                                           line_color=self.point_color,
                                           velocity=self.trace_velocity,
                                           **ptargs)
            elif self.mode == 'transect':
                self.canvas.new_transect_point(point_color=self.point_color,
                                               line_color=self.point_color,
                                               step=self.transect_step,
                                               **ptargs
                                               )
            elif self.mode=='polygon':
                self.canvas.new_polygon_point(point_color=self.point_color,
                                               line_color=self.point_color,
                                               use_convex_hull=self.use_convex_hull,
                                               **ptargs
                                               )
                
            else:
                npt = self.canvas.new_point(default_color=self.point_color,
                                            
                                            ** ptargs)

                self.info('added point {}:{:0.5f},{:0.5f} z={:0.5f}'.format(npt.identifier, npt.x, npt.y, npt.z))

    def load_stage_map(self, sm):
        if not (hasattr(sm, 'lines') and hasattr(sm, 'points')):
            return

        canvas = self.canvas
#        canvas.remove_point_overlay()
#        canvas.remove_line_overlay()
#        canvas.add_point_overlay()
#        canvas.add_line_overlay()
        
        canvas.clear_all()
        canvas.remove_markup_overlay()
        canvas.add_markup_overlay()
#        canvas.lines = []
#        canvas.points = []

        ptargs = dict(radius=0.05, 
                      vline_length=0.1, hline_length=0.1)
        for li in sm.lines:
            canvas._new_line = True
            for si in li:
                mi=si['mask'] if si.has_key('mask') else 0
                ai=si['attenuator'] if si.has_key('attenuator') else 0
                canvas.new_line_point(xy=si['xy'],
                                      z=si['z'],
                                      mask=mi, attenuator=ai,
                                      point_color=self.point_color,
                                       line_color=self.point_color,
                                       velocity=si['velocity'],
                                       **ptargs)
            canvas._new_line = True

        for pi in sm.points:
            mi=pi['mask'] if pi.has_key('mask') else 0
            ai=pi['attenuator'] if pi.has_key('attenuator') else 0
            canvas.new_point(xy=pi['xy'],
                             z=pi['z'],
                             mask=mi, attenuator=ai,
                             default_color=self.point_color,
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

            txt = dict()
            pts = [dict(identifier=pi.identifier,
                        z=float(pi.z),
                        mask=pi.mask,attenuator=pi.attenuator,
                        xy=[float(pi.x), float(pi.y)]
                        ) for pi in self.canvas.points]

            lines = []
            for li in self.canvas.lines:
                segments = []
                for i, pi in enumerate(li.points):
                    v = li.velocity_segments[i / 2]
                    segments.append(dict(xy=[float(pi.x), float(pi.y)], 
                                         z=float(pi.z),
                                         mask=pi.mask,
                                         attenuator=pi.attenuator,
                                         velocity=v))
                lines.append(segments)

            txt['points'] = pts
            txt['lines'] = lines
            with open(p, 'w') as f:
                f.write(yaml.dump(txt, default_flow_style=False))
#
#            with open(p, 'w') as f:
#                f.write('{},{}\n'.format('circle',0.1))
#                f.write('\n') #valid holes
#                f.write('\n') #calibration holes
#                for pt in self.canvas.points:
#                    f.write('p{:003n},{},{}\n'.format(pt.identifier,pt.x,pt.y))
#
#                f.write('='*80)
#                for li in self.canvas.lines:
#                    for i in range(0,len(li.points),2):
#                        p1=li.points[i]
#                        p2=li.points[i+1]
#                        v=li.velocity_segments[i]
#                        f.write('{:003n},{},{},{},{},{}'.format(li.identifier,
#                                                                p1.x, p1.y,
#                                                                p2.x, p2.y,
#                                                                v))
#                    f.write('\n')

#            sm = self.stage_map_klass(file_path=p)
#            self._stage_maps.append(sm)
#            self.canvas.save_points(p)
            self.stage_manager.add_stage_map(p)
            head,_tail=os.path.splitext(os.path.basename(p))
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
        v = View(
               VGroup(
                       Item('point_entry', label='Point'),
                       Item('line_entry', label='Line'),
                       Group(

                             Item('mode'),
                             Item('trace_velocity', visible_when='mode=="line"'),
                             Item('transect_step', visible_when='mode=="transect"'),
                             Item('use_convex_hull', visible_when='mode=="polygon"'),
                             Item('point_color', show_label=False),
                             HGroup(Item('show_hide', show_label=False,
                                         editor=ButtonEditor(label_value='show_hide_label')
                                         ),
                                    Item('program_points', show_label=False,
                                         editor=ButtonEditor(label_value='program_points_label')
                                         )
                                    ),
        #                elf._button_factory('program_points', 'program_points_label'),
                             VGroup(
                                 Item('accept_point', show_label=False),
                                 Item('load_points', show_label=False),
                                 Item('save_points', show_label=False),
                                 HGroup(Item('clear'), Item('clear_mode'), show_labels=False),
                                 Item('finish', show_label=False, enabled_when='mode=="line" and object.is_programming'),
                                 enabled_when='object.is_programming'
                                 ),
        #                     label='Points'
                             )
                      )
               )
        return v
