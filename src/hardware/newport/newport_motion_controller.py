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
#=============enthought library imports=======================
from traits.api import Enum, Instance
import apptools.sweet_pickle as pickle
#=============standard library imports ========================
import os
import time
import math
#=============local library imports  ==========================
from src.hardware.core.data_helper import make_bitarray
from src.hardware.motion_controller import MotionController
from src.helpers.gdisplays import gWarningDisplay
from newport_axis import NewportAxis
from newport_joystick import Joystick
from newport_group import NewportGroup

class NewportMotionController(MotionController):
    '''
    '''

    mode = Enum('normal', 'grouped')

    groupobj = Instance(NewportGroup)

    group_commands = True
    _trajectory_mode = None


    def initialize(self, *args, **kw):
        '''
        '''
        progress = kw['progress'] if 'progress' in kw else None



        #try to get x position to test comms
        if progress is not None:
            progress.change_message('Testing controller communications')



        r = True if self.get_current_position('x') is not None else False
        msg = 'Communications Fail' if not r else 'Communications Success'
        if progress is not None:
            progress.change_message(msg)

        #force group destruction
        self.destroy_group(force=True)

        #get and clear any error
        self.read_error()


        return r

    def axes_factory(self, config=None):
        if config is None:

            config = self.get_configuration(self.config_path)

        mapping = self.config_get(config, 'General', 'mapping')
        if mapping is not None:
            mapping = mapping.split(',')
        else:
            mapping = 'x,y,z'

        lp = self.config_get(config, 'General', 'loadposition')
        if lp is not None:
            loadposition = [float(f) for f in lp.split(',')]
        else:
            loadposition = [0, 0, 0]

        config_path = self.configuration_dir_path
        for i, a in enumerate(mapping):
            limits = [float(v) for v in config.get('Axes Limits', a).split(',')]
            na = self._axis_factory(config_path,
                                  name=a,
                                  id=i + 1,
                                  negative_limit=limits[0],
                                  positive_limit=limits[1],
                                  loadposition=loadposition[i]
                                  )

            self.axes[a] = na

    def load_additional_args(self, config):
        '''
        '''
        self.axes_factory(config)
#        mapping = self.config_get(config, 'General', 'mapping')
#        if mapping is not None:
#            mapping = mapping.split(',')
#        else:
#            return False
#
#        lp = self.config_get(config, 'General', 'loadposition')
#        if lp is not None:
#            loadposition = [float(f) for f in lp.split(',')]
#        else:
#            loadposition = [0, 0, 0]

        config_path = self.configuration_dir_path
#        for i, a in enumerate(mapping):
#            limits = [float(v) for v in config.get('Axes Limits', a).split(',')]
#            na = self._axis_factory(config_path,
#                                  name = a,
#                                  id = i + 1,
#                                  negative_limit = limits[0],
#                                  positive_limit = limits[1],
#                                  loadposition = loadposition[i]
#                                  )
#
#            self.axes[a] = na
        group = config.get('Optional', 'group')
        joystick = config.get('Optional', 'joystick')
        if group:
            self.load_optional_parameters(config_path, '{}.cfg'.format(group), 'group', '''NEWPORT GROUP PARAMETERS NOT SPECIFIED. YOU WILL NOT BE
ABLE TO PERFORM GROUPED MOVES I.E. LINEAR OR CIRCULAR
            ''')
        if joystick:

            self.load_optional_parameters(config_path, '{}.txt'.format(joystick), 'joystick', '''NEWPORT JOYSTICK PARAMETERS NOT SPECIFIED. YOU WILL NOT BE
ABLE TO USE THE HARDWARE JOYSTICK
            ''')

        #the esp 300 doesnt like grouped commands 
        #ie 1PA1.0;2PA1.0
        self.set_attribute(config, 'group_commands', 'General', 'group_commands', cast='boolean', optional=True)

        #set the drive calibration values

        return True

    def load_optional_parameters(self, base, path, paramname, warning):
        '''
        '''
        p = os.path.join(base, path)
        if os.path.isfile(p):
            with open(p, 'r') as f:
                func = getattr(self, 'load_{}_parameters'.format(paramname))
                func(f, p)
        else:
            self.warning(warning)

    def load_joystick_parameters(self, f, p):
        '''
        '''

        self.joystick = Joystick(parent=self)
        self.joystick.load_parameters(f)

#        self.joystick_bits=[]

    def load_group_parameters(self, f, p):
        '''
        '''
        self.groupobj = NewportGroup()
        self.groupobj.load(p)


    def load_commands_from_file(self, p):
        '''
        '''

        with open(p, 'r') as f:
            for line in f:
                line = line[:-1]
                if line:
                    if line[0] != '#':
                        self.ask(line)

    def save_axes_parameters(self, axis=None):
        '''
        '''
        if axis is None:
            axes = self.axes.itervalues()
        else:
            axes = [axis]

        for a in axes:
            a.save()

        com = 'SM'
        return self.tell(com)

    def enable_joystick(self):
        '''
        '''
        self.joystick.enable()

    def disable_joystick(self):
        '''
        '''
        self.joystick.disable_laser()
    def get_xy(self):

        v = self.ask('1TP?;2TP?', verbose=False)
        if v is None:
            return 0, 0

        return map(float, v.split('\n'))

    def get_current_position(self, aid):
        ''' 
        '''
        if isinstance(aid, str):
            if aid in self.axes:
                ax = self.axes[aid]
                aid = ax.id
                axis = ax.name
            else:
                return
        else:
            ax = self._get_axis_by_id(aid)
            axis = ax.name

        cmd = self._build_query('TP', xx=aid)
        f = self.ask(cmd,
                     verbose=False
                     )

        if f != 'simulation' and f is not None:
            try:
                f = float(f)

                f = self._sign_correct(f, axis, ratio=False) / ax.drive_ratio
            except ValueError:
                f = None
        else:
#            time.sleep(0.5)
            f = getattr(self, '_{}_position'.format(axis))

        return f

    def relative_move(self, key_direction):
        #move one pixel in the specified direction

        if key_direction == 'Left':
            ax_key = 'x'
            direction = 1
        elif key_direction == 'Right':
            ax_key = 'x'
            direction = -1
        elif key_direction == 'Down':
            ax_key = 'y'
            direction = -1
        elif key_direction == 'Up':
            ax_key = 'y'
            direction = 1

        ax = self.axes[ax_key]

        v1 = self.parent.canvas.map_data((0, 0))
        v2 = self.parent.canvas.map_data((1, 1))


        if ax_key == 'y':
            v = (v2[1] - v1[1]) * direction * ax.sign + self._y_position
#            v = self._y_position + v
#            x = self._x_position
#            y = v

        else:
            v = (v2[0] - v1[0]) * direction * ax.sign + self._x_position
#            v = self._x_position + v
#            x = v
#            y = self._y_position

        #self.parent.canvas.set_desired_position(x, y)
        #self.parent.canvas.set_stage_position(x, y)

        self.single_axis_move(ax_key, v, block=False, mode='relative', update=False)
        setattr(self, '_{}_position'.format(ax_key), v)


    def multiple_point_move(self, points, nominal_displacement=0.5):

        self.timer = self.timer_factory()
        #use a nominal displacement to set the motion params
        self.configure_group(True, displacement=nominal_displacement)
        cmd = self._build_command('HQ', xx=self.groupobj.id, nn=10)
        self.tell(cmd, verbose=True)

        avaliable_spaces = 10
        while 1:
            #isue the first 10 points and wait
            for x, y in points[:avaliable_spaces]:
                #sign correct each point
                x = self._sign_correct(x, 'x')
                y = self._sign_correct(y, 'y')
                cmd = self._build_command('HL', xx=self.groupobj.id, nn='{:0.5f},{:0.5f}'.format(x, y))
                self.tell(cmd, verbose=True)

            waiting = True
            resp = 0
            while waiting and not self.simulation:
                cmd = self._build_query('HQ', xx=self.groupobj.id)
                resp = self.ask(cmd, verbose=False)
                if resp is not None:
                    resp = resp.strip()
                    resp = int(resp)
                    waiting = True if resp < 6 else False
                else:
                    break
                time.sleep(0.05)
            points = points[avaliable_spaces:]
            avaliable_spaces = resp
            if not points:
                break

    def linear_move(self, x, y, **kw):

        #calc the displacement
        dx = self._x_position - x
        dy = self._y_position - y
        tol = 0.0001
        d = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
        if abs(dx - 0) < tol:
            if 'grouped_move' in kw:
                kw.pop('grouped_move')

            self.info('x displacement {} doing a hack axis move'.format(dx))
#            points = [(x + 0.001, y / 2.0), (x, y)]
#            self.multiple_point_move(points, nominal_displacement = d)
            self.single_axis_move('y', y, **kw)
            self._y_position = y
            return
        if abs(dy - 0) < tol:
            if 'grouped_move' in kw:
                kw.pop('grouped_move')
            self.info('y displacement {} doing a hack axis move'.format(dy))
#            points = [(x / 2.0, y + 0.001), (x, y)]
#            self.multiple_point_move(points, nominal_displacement = d)
            self.single_axis_move('x', x, **kw)
            self._x_position = x
            return

        errx = self._validate(x, 'x', cur=self._x_position)
        erry = self._validate(y, 'y', cur=self._y_position)
        if errx is None and erry is None:
            return 'invalidate position {},{}'.format(x, y)

        tol = 0.001 #should be set to the motion controllers resolution 
        if d > tol:
            kw['displacement'] = d
            self.parent.canvas.set_desired_position(x, y)
            self._x_position = x
            self._y_position = y

            self.timer = self.timer_factory()
            self._linear_move_(dict(x=x, y=y), **kw)
        else:
            self.info('displacement of move too small {} < {}'.format(d, tol))

    def single_axis_move(self, key, value, block=False, mode='absolute', update=True, **kw):
        '''
        '''
        x = None
        y = None
        ax = self.axes[key]
        aid = ax.id
        if self.groupobj is not None:
            if aid in map(int, self.groupobj.axes):
                self.destroy_group()

        if mode == 'absolute':
            cmd = 'PA'
        else:
            cmd = 'PR'

        cmd = self._build_command(cmd, xx=aid,
                                  nn='{:0.5f}'.format(self._sign_correct(value, key) * ax.drive_ratio))
        func = None

        if key != 'z':
            if key == 'x':
                x = value
                y = self._y_position
                o = self._x_position
            else:
                x = self._x_position
                y = value
                o = self._y_position

            if self._validate(value, key, cur=o) is  None:
                value = float(value)
                if abs(value - o) <= 0.001:
                    return 'At desired position. cur={} desired={}'.format(o, value)
                return 'invalid position {}'.format(value)

            self.parent.canvas.set_desired_position(x, y)

            dx = self._x_position - self._sign_correct(x, 'x')
            dy = self._y_position - self._sign_correct(y, 'y')

            disp = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))

            if self._check_motion_parameters(disp, ax):
                self._set_single_axis_motion_parameters(ax)
        else:
            func = self._z_inprogress_update

        if block:
            block = key

        if update:
#        if update and not block:
            self.timer = self.timer_factory(func=func)
        else:
            if x is not None and y is not None:
                self.parent.canvas.set_stage_position(x, y)
            else:
                self._z_position = value
                self.z_progress = value

        self._axis_move(cmd, block=block)

    def multiple_axis_move(self, axes_list, block=False):
        '''
            block - wait for move to complete before returning control
        '''
        self.configure_group(False)

        cmd = ';'.join(['{}PA{:0.3f}'.format(ax, val)
#                                  self._sign_correct(val,
#                                                    self._get_axis_by_id(ax).name))

                for ax, val in axes_list])



        self._axis_move(cmd, block=block)

    def arc_move(self, cx, cy, angle, block=True, sign_correct=True):
        ''' 
            the radius of the resultant arc is
            the distance from the center to the current point
            
        '''
        self.configure_group(True)

        if self.mode == 'group':
            if sign_correct:
                cx = self._sign_correct(cx, 'x')
                cy = self._sign_correct(cy, 'y')

            cmd = '1HC{:0.3f,:0.3f,:0.3f}'.format (cx, cy , angle)
            self.tell(cmd)

        if block:
            self._block_()

    def get_load_position(self):

        x = self.axes['x'].loadposition
        y = self.axes['y'].loadposition
        z = self.axes['z'].loadposition
        return x, y, z

    def home(self, axes, search_mode=4, block=True):
        '''
        '''
        #manual 3-104
        #If nn = 0, the axes will search for zero position count.
        #If nn = 1, the axis will search for combined Home and 
        #Index signal transitions. 
        #If nn = 2, the axes will search for Home signal 
        #transition only. 
        #If nn = 3, the axes willsearch for positive limit signal transition. 
        #If nn = 4, the axes will search for negative limit signal
        # transition. 
        #If nn = 5, the axes will search for positive limit and index signal
        # transition. 
        #If nn = 6, the axes will search for negative limit and
        # index signal transition.

        #destroy the grouping
        self.destroy_group(force=True)


#        cmd = ';'.join(['{}OR{{}}'.format(k.id) for k in self.axes.itervalues()])
        #if all:
#            cmd = ';'.join(['{}OR{{}}'.format(k.id) for k in self.axes.itervalues()])
        cmd = ';'.join([self._build_command('OR', a.id, nn=search_mode if a.name.lower() != 'z' else 3)
                         for a in self.axes.itervalues() if a.name in axes])


        #force z axis home positive 
        #cmd = '1OR{};2OR{};3OR{}' .format(search_mode, search_mode, 3)
#        cmd = cmd.format(*[search_mode if v.id != 3 else 3 for k, v in self.axes.iteritems()])
#        cmd = cmd.format(*[search_mode if v.id != 3 else 3 for v in axes])
#        if 'z' in axes:
#            axis = self.axes.keys().index('z')
#            search_mode = 3

#            cmd = self._build_command('OR', xx = axis, nn = )

#        self.timer = self.timer_factory()
        if self.group_commands:
            self.tell(cmd)

            if block:
                self._block_()
        else:
            for c in cmd.split(';'):
                self.tell(c)
                if block:
                    self._block_()

    def block_group(self, n=10):
        cmd = '1HQ%i' % n
        self.tell(cmd)

        while self.group_moving() and not self.simulation:
            time.sleep(0.1)

    def group_moving(self):
#        cmd = '1HS?'

        cmd = self._build_query('HS', xx=self.groupobj.id)
        m = True if self.ask(cmd) == '0' else False
        return m

    def stop(self, ax_key=None):

        if self.timer is not None:
            self.timer.Stop()

        if self.mode == 'grouped':
            #check group is moving

            while self.group_moving() and not self.simulation:
                cmd = '1HS'
                self.tell(cmd)
                time.sleep(0.1)
        else:
            if isinstance(ax_key, str):
                cmd = self._build_command('ST', xx=self.axes[ax_key].id)
            else:
                cmd = 'ST'
            self.tell(cmd)

    def destroy_group(self, force=False, mode=1):
        '''
        '''
        if self.mode == 'grouped' or force:
            self.info('destroying group')
            com = '1HX'
            self.tell(com)


        self.set_trajectory_mode(mode)
        self.mode = 'normal'
#            if self.speed_mode == 'low':
#                self.set_low_speed()

    def set_home_position(self, **kw):

        cmd = []
        for k in kw:
            if k in self.axes:
                id = self.axes[k].id
                cmd.append(self._build_command('SH', xx=id, nn=kw[k]))

        self.tell(';'.join(cmd))

    def define_home(self, axis=None):
        '''
        '''
        if axis is not None:
            id = self.axes[axis].id
            cmd = self._build_command('DH', xx=id, nn=0)
        else:
            cmd = []
            for k in ['x', 'y']:
                id = self.axes[k].id
                cmd.append(self._build_command('DH', xx=id, nn=0))
            cmd = ';'.join(cmd)

        self.tell(cmd)

        err = self.read_error()
        if err is None:
            err = True

        return err

    def set_trajectory_mode(self, mode):
        '''
            modes see ESP301 manual page 3-137
        
            1. trapezoidal
            2. s-curve
            3. jog mode
            4. slave to master's desired position (trajectory)
            5. slave to master's actual position (feedback)
            6. slave to master's actual velocity for jogging
        '''
        if mode is self._trajectory_mode:
            return

        self._trajectory_mode = mode
        coms = []
        for k in self.axes:
            coms.append(self._build_command('TJ', xx=self.axes[k].id, nn=mode))

        if self.group_commands:
            com = ';'.join(coms)
            self.tell(com)
        else:
            for c in coms:
                self.tell(c)

    def read_assigned_groups(self):
        '''
        '''
        com = 'HB'
        r = self.ask(com)
        if not r or r == 'simulation':
            r = []

        return r

    def read_error(self):
        error = None
#        cmd = 'TB?'
        cmd = self._build_query('TB')
        r = self.ask(cmd)
        if r is not None and r != 'simulation':
            eargs = r.split(',')
            try:
                error_code = int(eargs[0])
                error_msg = eargs[-1]
                if error_code == 0:
                    error = None
                else:
                    error = error_code
                    gWarningDisplay.add_text('%s - %s' % (self.name, error_msg))
            except:
                pass
        return error
    def set_group_motion_parameters(self, acceleration=None, deceleration=None, velocity=None):
        if self.groupobj is not None:
            if acceleration is not None:
                self.groupobj.acceleration = acceleration
            if deceleration is not None:
                self.groupobj.acceleration = deceleration
            if velocity is not None:
                self.groupobj.velocity = velocity

    def _check_motion_parameters(self, displacement, obj):
        if displacement <= 0:
            return
        if obj.calculate_parameters:
            change, nv, ac, dc = self.motion_profiler.check_motion(displacement, obj)
            if change:
                obj.trait_set(_acceleration=ac,
                                        _deceleration=dc,
                                        _velocity=nv)
        else:
            change = (obj.machine_acceleration != obj.acceleration or
                      obj.machine_deceleration != obj.deceleration or
                      obj.machine_velocity != obj.velocity)
        return change

    def configure_group(self, group, displacement=None, velocity=None, **kw):
        gobj = self.groupobj
        if not gobj and group:
            self.logger.warn('GROUPED MOVE NOT ENABLED')
            self.mode = 'normal'
            return False

        if group:
            if velocity is not None:
                gobj.velocity = velocity

            change = self._check_motion_parameters(displacement, gobj)

        if self.mode == 'grouped':
            if not group:
                self.destroy_group()
            elif change: #the group needs a motion parameter change
                self._set_axis_grouping(new_group=False)
        else: # mode==normal
            if group:
                self._set_axis_grouping()
            else:
                self.destroy_group()

        return True

    def at_velocity(self, axkey, event, tol=0.25):
        if not self.simulation:
            desired_velocity = float(self.ask(self._build_query('VA', xx=self.axes[axkey].id)))
            av = self.read_actual_velocity(axkey)
            while av is not None and abs(abs(av) - desired_velocity) > tol:
                av = self.read_actual_velocity(axkey)
                time.sleep(0.01)

            event.clear()
            desired_velocity = 0
            while av is not None and abs(abs(av) - desired_velocity) > tol:
                av = self.read_actual_velocity(axkey)
                time.sleep(0.01)

        event.set()

    def read_actual_velocity(self, axkey):
        ax = self.axes[axkey]
#        self._build_command('TV', xx = ax.id, nn = '?')
        cmd = self._build_query('TV', xx=ax.id)
        v = self.ask(cmd, verbose=False)
        if v is not None:
            return float(v)


    def _set_axis_grouping(self, new_group=True):
        #check group_parameters are acceptable
        if new_group:
            msg = 'setting new group'
            self.set_trajectory_mode(1)

        else:
            msg = 'changing group parameters'
        self.info(msg)
        self.mode = 'grouped'

        cmd = self.groupobj.build_command(new_group)
        if self.group_commands:
            self.tell(cmd)
        else:
            for c in cmd.split(';'):
                self.tell(c)
                time.sleep(0.1)
                #self.read_error()
                #time.sleep(0.1)

    def _set_single_axis_motion_parameters(self, axis=None, pdict=None):
        '''
           
        '''
        pmap = dict(velocity='VA',
                  acceleration='AC',
                  deceleration='AG')


        if pdict:
            axis = self.axes[pdict['key']]
            cmds = []
            for k in pdict.keys():
                if k is not 'key':
                    cmds.append('{}{}{}'.format(axis.id, pmap[k], pdict[k]))

            cmd = ';'.join(cmds)
        else:
            param_coms = [('VA', 'velocity'),
                        ('AC', 'acceleration'),
                        ('AG', 'deceleration')]
            pdict = dict(velocity=axis.velocity,
                       acceleration=axis.acceleration,
                       deceleration=axis.deceleration)

            cmd = ';'.join(['{:n}{}{{{}:0.2f}}'.format(*(axis.id,) + p) for p in param_coms])

        #ex cmd
        #1VA1.00;1AC2.00;1AG2.00
            cmd = cmd.format(**pdict)

        if self.group_commands:
            self.tell(cmd)
        else:
            for c in cmd.split(';'):
                self.tell(c)
                time.sleep(0.1)

    def _get_axis_by_id(self, aid):
        '''
        '''
        for k in self.axes:
            a = self.axes[k]
            if a.id == aid:
                return a

    def _linear_move_(self, kwargs, block=False, grouped_move=True, sign_correct=True, **kw):
        '''
        '''
        self.configure_group(grouped_move, **kw)
        for k in kwargs:
            key = k[0]
            if sign_correct:
#                axis = self.axes[key]
                val = self._sign_correct(kwargs[k], key, ratio=True)
                kwargs[k] = val

        if self.mode == 'grouped':

            gid = self.groupobj.id


            st = '{:n}HL{x:0.5f},{y:0.5f}'.format(gid, **kwargs)
#            this switch is accomplished by the group_parameter axes orer 
#            axes=2,1
#            if self.axes['x'].id == 2:
#                st = '{:n}HL{y:0.3f},{x:0.3f}'.format(id, **kwargs)

            self.tell(st, verbose=True)
        else:

            self.multiple_axis_move([
                                     (self.axes['y'].id, kwargs['y']),
                                     (self.axes['x'].id, kwargs['x'])
                                     ])

        if block:
            self._block_()
            self.info('move to {x:0.5f},{y:0.5f} complete'.format(**kwargs))
            self.update_axes()

    def _axis_move(self, com, block=False):
        '''
        '''

        if self.group_commands:
            self.tell(com)
        else:
            for c in com.split(';'):
                self.tell(c)
                time.sleep(0.1)

        if block:
            self._block_(axis=block)

    def _sign_correct(self, val, key, ratio=True):
        '''
        '''
        axis = self.axes[key]
        r = 1
        if ratio:
            r = axis.drive_ratio

        return val * axis.sign * r

    def _block_(self, axis=None, event=None):
        '''
        '''
        if event is not None:
            event.clear()

        while self._moving_(axis=axis):
            # is the sleep necessary and ehat period 
            time.sleep(0.1)

        if event is not None:
            event.set()

    def _moving_(self, axis=None):
        '''
            use TX to read the controllers state.
            see manual 3-141
            return value of P==0101000
                      bits     7654321 
            7,6,5=reserved
            4=trajectory executing yes=1
            
        '''
        if axis is not None:
            if isinstance(axis, str):
                axis = self.axes[axis].id

            if self.mode == 'grouped':
                return self.group_moving()
            else:
                for _ in range(5):
                    r = self.ask(self._build_command('MD?', xx=axis),
                                verbose=False
                                )
                    if r in ['0', '1']:
                        break
#                    time.sleep(0.25)
#                time.sleep(0.5)
                return True if r == '0' else False

        moving = False
        if not self.simulation:
#        else:
            retries = 5
            i = 0
            r = ''
            while not r or i > retries:
                r = self.ask(self._build_command('TX'),
                         verbose=False
                         )
                i += 1

            if r is not None:
                if len(r) > 0:
                    r = r[0]
                    controller_state = ord(r)

                    cs = make_bitarray(controller_state, width=8)
                    moving = cs[3] == '1'
            else:
                moving = False
        else:
            time.sleep(0.5)

        return moving

    def _build_command(self, command, xx=None, nn=None):
        '''
        '''
        if isinstance(nn, list):

            nn = ','.join([str(n) for n in nn])

        cmd = '{}'
        args = (command,)
        if xx is not None:
            cmd += '{}'
            args = (xx, command)
        if nn is not None:
            cmd += '{}'
            args = (xx, command, nn)

        return cmd.format(*args)

    def _build_query(self, command, xx=' '):
        return self._build_command(command, xx=xx, nn='?')

    def _axis_factory(self, path, **kw):
        '''
        '''
        na = NewportAxis(parent=self,
                       **kw
                         )

        p = na.load(path)
        if p:
            with open(p, 'r') as f:
                na = pickle.load(f)
                na.parent = self
                na.loaded = True

        return na

    def _joystick_inprogress_update(self):
        '''
        '''

        for a in ['x', 'y', 'z']:
            val = self.get_current_position(a)
            setattr(self, '_%s_position' % a, val)

        self.parent.canvas.set_stage_position(self._x_position, self._y_position)
#======================EOF========================================
#def jog_move(self, c):
#
#        if c == 'Left':
#            ax_key = 'x'
#            direction = -1
#        elif c == 'Right':
#            ax_key = 'x'
#            direction = 1
#        elif c == 'Down':
#            ax_key = 'y'
#            direction = -1
#        elif c == 'Up':
#            ax_key = 'y'
#            direction = 1
#
#        self.destroy_group(mode = 1)
#
#        ax = self.axes[ax_key]
#        direction = '+' if direction * ax.sign == 1 else '-'
#
#        cmd = self._build_command('MV', xx = ax.id, nn = direction)
#        self.tell(cmd)
#
#        pos = self.get_current_position(ax_key)
#        if pos is not None:
#            setattr(self, '_{}_position'.format(ax_key), pos)
