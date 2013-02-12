#===============================================================================
# Copyright 2011 Jake Ross
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
#from traits.api import HasTraits, on_trait_change, Str, Int, Float, Button
#from traitsui.api import View, Item, Group, HGroup, VGroup

#============= standard library imports ========================

#============= local library imports  ==========================
from aerotech_axis import AerotechAxis
from src.hardware.motion_controller import MotionController
import time
from src.hardware.core.data_helper import make_bitarray


ACK = chr(6)
NAK = chr(15)
EOS = chr(10)


class AerotechMotionController(MotionController):
    def initialize(self, *args, **kw):
        '''
        '''
        self._communicator.write_terminator = None
        self.tell('##')
        self._communicator.write_terminator = chr(13)
        self._communicator.read_delay = 25
        self.enable()
        #self.home()
#        for a in self.axes.itervalues():
#            a.load_parameters()

        return True

    def load_additional_args(self, config):
        '''

        '''
        self.axes_factory()
        return True
    
    def xy_swapped(self):
        if self.axes.has_key('y'):
            return self.axes.keys().index('y') == 0
        
    def linear_move(self, x, y, sign_correct=True, block=False, velocity=None,**kw):
        errx = self._validate(x, 'x', cur=self._x_position)
        erry = self._validate(y, 'y', cur=self._y_position)
        if errx is None and erry is None:
            return 'invalid position {},{}'.format(x, y)

        self.parent.canvas.set_desired_position(x, y)
        self._x_position = x
        self._y_position = y

        nx = x - self.get_current_position('x')
        ny = y - self.get_current_position('y')
        if sign_correct:
            nx = self._sign_correct(nx, 'x', ratio=False)
            ny = self._sign_correct(ny, 'y', ratio=False)

        self.timer = self.timer_factory()
        x=self.axes['x']
        y=self.axes['y']
        
        if velocity is not None:
            xv=yv=velocity
        else:
            xv=x.velocity
            yv=y.velocity
        
        if abs(nx)>1:
            xv=xv*0.5
        if abs(nx)>1:
            yv=yv*0.5
            
        if self.xy_swapped():
            cmd = 'ILI X{} Y{} XF{} YF{}'.format(ny, nx, xv, yv)
        else:
            cmd = 'ILI X{} Y{} XF{} YF{}'.format(nx, ny, xv, yv)

        self.ask(cmd, handshake_only=True)
        if block:
            self.block()

    def set_single_axis_motion_parameters(self, axis=None, pdict=None):
        if pdict is not None:
            key = pdict['key']
            self.axes[key].velocity = pdict['velocity']

    def single_axis_move(self, key, value, block=False):
        '''
        '''
        nkey = self._get_axis_name(key)
        axis = self.axes[nkey]
        name = axis.name.upper()
        cp = self.get_current_position(key)
        if self._validate(value, nkey, cp) is not None:
            setattr(self, '_{}_position'.format(key), value)
            nv = value - cp

            nv = self._sign_correct(nv, key, ratio=False)
            cmd = 'IIN {}{} {}F{}'.format(name, nv, name, axis.velocity)

            if name == 'Z':
                func = self._z_inprogress_update
            else:
                func = self._inprogress_update

            self.ask(cmd, handshake_only=True)
            self.timer = self.timer_factory(func=func)

            if block:
                self.block()
#
#    def _relative_move(self, axes, values):
#        '''
#        '''
#
#        cmd = 'INDEX'
#
#        cmd = self._build_command(cmd, axes, values=values)
#        resp = self.ask(cmd)
#        return self._parse_response(resp)
    def block(self, axis=None):
        time.sleep(0.25)
#        for i in range(100):
#            self._moving()
        while self._moving_():
            time.sleep(0.5)

    def _moving_(self):
        cmd = 'Q'
        sb = self.ask(cmd, verbose=False)
        if sb is not None:
        #cover status bit to binstr
            b = make_bitarray(int(sb))
            return int(b[2])

    def _get_axis_name(self, axis):
#        print self.axes.keys(),self.axes.keys().index('y')
        if axis in ('x', 'y'):
            if self.xy_swapped():
#            if self.axes.keys().index('y') == 0:
                if axis == 'y':
                    axis = 'x'
                else:
                    axis = 'y'
        return axis

    def get_current_position(self, axis, verbose=False):
        naxis = self._get_axis_name(axis)

        cmd = 'P{}'.format(naxis)
        pos = self.ask(cmd, verbose=verbose)
        if pos is not None:
            pos = float(pos)
            pos = self._sign_correct(pos, axis)
#            setattr(self, '_{}_position'.format(axis), pos)
        else:
            pos = 0

        return pos

    def enable(self, axes=None):
        '''
        '''

        cmd = 'IEN'
        axes = self._get_axes_name_list(axes)
        cmd = '{} {}'.format(cmd, axes)
        resp = self.ask(cmd, handshake_only=True)

    def _get_axes_name_list(self, axes):
        if axes is None:
            axes = self.axes.keys()
        axes = map(str.upper, axes)
        return ' '.join(axes)
#    def disable(self):
#        '''
#        '''
#
#        cmd = 'DI'
#
#        axes = ['X', 'Y', 'Z']
#        axes = ' '.join(axes)
#        cmd = self._build_command(cmd, axes)
#        self.tell(cmd)
#        #resp=self.ask(cmd)
#        #return self._parse_response(resp)
    def define_home(self, axes=None):
        cmd = 'ISO HOME'
        axes = self._get_axes_name_list(axes)

        cmd = '{} {}'.format(cmd, axes)
        resp = self.ask(cmd, handshake_only=True)

    def home(self, axes=None):
        '''
        '''
        cmd = 'IHO'
        axes = self._get_axes_name_list(axes)

        cmd = '{} {}'.format(cmd, axes)
        resp = self.ask(cmd, handshake_only=True)
        time.sleep(1)
        self.block()
        time.sleep(1)
        self.linear_move(25, 25, sign_correct=False)
        self.block()
        self.define_home()

#
#    def get_current_position(self, key):
#        '''
#
#        '''
#        cmd = 'P'
#        axis = self.axes[key]
#        rtype = 4  # absolute command posisiton
#        axis = '%s%i' % (axis.name, rtype)
#        cmd = self._build_command(cmd, axis, remote=False)
#        r = self.ask(cmd)
#
#        return r
#
#    def set_parameter(self, pid, value):
#        '''
#
#        '''
#        cmd = 'WP%i,%s' % (pid, value) + EOS
#        r = self.ask(cmd)
#        self._ensure_ack(r)
#
#    def save_parameters(self):
#        '''
#        '''
#        cmd = 'SP'
#        r = self.ask(cmd)
#        self._ensure_ack(r)
#
#    def _ensure_ack(self, r):
#        '''
#
#        '''
#        r = r.strip()
#        if not r == ACK:
#            w = r
#            if r == NAK:
#                w = 'NAK'
#
#            self.warning('%s' % w)
#
#    def _build_command(self, cmd, axes, values=None, remote=True):
#        '''
#        '''
#
#        if values is None:
#            parameters = axes
#        else:
#            parameters = ' '.join(['{}{}'.format(*pi) for pi in zip(axes, values)])
#
#        if cmd.startswith('P'):
#            args = (cmd, parameters, EOS)
#            cmd = ''.join(args)
#        else:
#            args = (cmd, parameters, EOS)
#            cmd = '{} {}{}' % args
#
#        if remote:
#            cmd = EIC + cmd
#        return cmd
#
#    def _moving_(self):
#        '''
#        '''
##        n='5'
##        status=self._get_status(n)
##
##
##        status=[s for s in status]
##        status.reverse()        
##        #1 not in position
##        #0 in position
##        return status[4] or status[5] or status[6]
##    
#        pass
#
#    def _get_status(self, n):
#        '''
#
#        '''
#        cmd = 'PS'
#
#        cmd = self._build_command(cmd, n, remote=False)
#        r = self.ask(cmd)
#        if self.simulation:
#            r = '4'
#
#        return self._parse_status(r)
#
#    def _parse_status(self, r):
#        '''
#
#        '''
#
#        r = self._parse_response(r)
#        return make_bitarray(int(r), width=32)
#
#    def _parse_response(self, resp):
#        '''
#
#        '''
#        if resp is not None:
#            return resp.strip()
    def ask(self, cmd, **kw):
        return super(AerotechMotionController, self).ask(cmd, handshake=[ACK, NAK], **kw)

    def _axis_factory(self, path, **kw):
        '''
        '''
        a = AerotechAxis(parent=self, **kw)
        p = a.load(path)
        return a

#if __name__ == '__main__':
#    amc = Aero


#============= EOF ====================================
