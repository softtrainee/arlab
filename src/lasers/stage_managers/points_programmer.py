from traits.api import HasTraits, Color, Button, Event, Property, \
    Any, List, Bool, Enum, Float, Int
from traitsui.api import View, Item, ButtonEditor, Group, HGroup, VGroup
from src.paths import paths
#from src.lasers.stage_managers.stage_map import StageMap
from src.loggable import Loggable
import yaml
from src.managers.manager import Manager

'''
    add transect programming. define two end points, define step distance. 
    save each step as a point
'''
class PointsProgrammer(Manager):

    canvas = Any
    program_points = Event
    is_programming = Bool
    finish = Button

    program_points_label = Property(depends_on='is_programming')
    load_points = Button
    save_points = Button
    clear = Button
    clear_mode = Enum('all', 'all lines', 'all points', 'current line',
                    'current point', 'last point'
                    )
    accept_point = Button
    stage_map_klass = Any
    mode = Enum('transect', 'point', 'line')

    point_color = Color('green')

    trace_velocity = Float
    point_entry = Property(Int(enter_set=True, auto_set=False))
    point = Any
    line_entry = Property(Int(enter_set=True, auto_set=False))
    line = Any
    transect_step = Float(1, enter_set=True, auto_set=False)

    def _set_line_entry(self, v):
        pts = self.canvas.lines
        pp = next((pi for pi in pts if pi.identifier == str(v)), None)
        if pp is not None:
            self.line = pp

    def _get_line_entry(self):
        p = ''
        if self.line:
            p = self.line.identifier
        return p

    def _set_point_entry(self, v):
        pts = self.canvas.points
        pp = next((pi for pi in pts if pi.identifier == str(v)), None)
        if pp is not None:
            self.point = pp

    def _get_point_entry(self):
        p = ''
        if self.point:
            p = self.point.identifier
        return p
#===============================================================================
# handlers
#===============================================================================
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
            self.is_programming = False
            self.canvas.remove_point_overlay()
            self.canvas.remove_line_overlay()
        else:
            self.is_programming = True

            self.canvas.add_point_overlay()
            self.canvas.add_line_overlay()

#        if not self.canvas.markup:
#            self.canvas.tool_state = 'point'
#        else:
#            self.canvas.tool_state = 'select'
#            if self.canvas.selected_element:
#                self.canvas.selected_element.set_state(False)
#                self.canvas.request_redraw()
#        self.canvas.markup = not self.canvas.markup
    def _finish_fired(self):
        self.canvas.new_line = True

    def _accept_point_fired(self):
        ptargs = dict(radius=0.05, vline_length=0.1, hline_length=0.1)
        if not self.canvas.point_exists():
            if self.mode == 'line':
                self.canvas.new_line_point(point_color=self.point_color,
                                           line_color=self.point_color,
                                           velocity=self.trace_velocity,
                                           **ptargs)
            if self.mode == 'transect':
                self.canvas.new_transect_point(point_color=self.point_color,
                                               line_color=self.point_color,
                                               step=self.transect_step,
                                               **ptargs
                                               )
            else:
                npt = self.canvas.new_point(default_color=self.point_color,
                                            **ptargs)
                self.info('added point {}:{:0.5f},{:0.5f}'.format(npt.identifier, npt.x, npt.y))

    def load_stage_map(self, sm):
        if not (hasattr(sm, 'lines') and hasattr(sm, 'points')):
            return

        canvas = self.canvas
        canvas.remove_point_overlay()
        canvas.remove_line_overlay()
        canvas.add_point_overlay()
        canvas.add_line_overlay()
        canvas.lines = []
        canvas.points = []

        ptargs = dict(radius=0.05, vline_length=0.1, hline_length=0.1)
        for li in sm.lines:
            canvas.new_line = True
            for si in li:
                canvas.new_line_point(xy=si['xy'],
                                      point_color=self.point_color,
                                       line_color=self.point_color,
                                       velocity=si['velocity'],
                                       **ptargs)
            canvas.new_line = True

        for pi in sm.points:
            canvas.new_point(xy=pi['xy'],
                             default_color=self.point_color,
                                    **ptargs)

        canvas.invalidate_and_redraw()

    def _load_points_fired(self):
        p = self.open_file_dialog(default_directory=paths.user_points_dir)
        if p:
            sm = self.stage_map_klass(file_path=p)
            self.load_stage_map(sm)
            self.is_programming = True

#            self.canvas.load_points_file(p)

    def _save_points_fired(self):
        p = self.save_file_dialog(default_directory=paths.user_points_dir)

        if p:
            if not p.endswith('.yaml'):
                p = '{}.yaml'.format(p)

            txt = dict()
            pts = [dict(identifier=pi.identifier,
                      xy=[pi.x, pi.y]
                      )

                 for pi in self.canvas.points]

            lines = []
            for li in self.canvas.lines:
                segments = []
                for i, pi in enumerate(li.points):
                    v = li.velocity_segments[i / 2]
                    segments.append(dict(xy=[pi.x, pi.y], velocity=v))
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

            sm = self.stage_map_klass(file_path=p)
#            
            self._stage_maps.append(sm)


#            self.canvas.save_points(p)
    def _get_program_points_label(self):
        return 'Hide' if self.is_programming else 'Show'

    def _mode_default(self):
        return 'transect'#'point'

    def _clear_mode_default(self):
        return 'all'

    def traits_view(self):
        v = View(
               VGroup(
                       Item('point_entry', label='Point'),
                       Item('line_entry', label='Line'),
                       Group(

                             Item('mode'),
                             Item('trace_velocity'),
                             Item('transect_step'),
                             Item('point_color', show_label=False),
                             Item('program_points', show_label=False,
                                  editor=ButtonEditor(label_value='program_points_label')),
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
