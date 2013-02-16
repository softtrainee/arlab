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
from traits.api import Str, Any, Bool, DelegatesTo, Dict, Property
from pyface.timer.do_later import do_later
from pyface.wx.dialog import confirmation
#============= standard library imports ========================
import time
import os
import inspect
import hashlib
from threading import Thread, Event
#============= local library imports  ==========================
from src.pyscripts.wait_dialog import WaitDialog
from src.loggable import Loggable


from Queue import Queue, Empty
from globals import globalv
class DummyManager(Loggable):
    def open_valve(self, *args, **kw):
        self.info('open valve')

    def close_valve(self, *args, **kw):
        self.info('close valve')


class GosubError(Exception):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return 'GosubError: {} does not exist'.format(self.path)

def KlassError(Exceotion):
    def __init__(self, klass):
        self.klass = klass

    def __str__(self):
        return 'KlassError: {} does not exist'.format(self.klass)


class PyscriptError(Exception):
    def __init__(self, err):
        self.err = err
    def __str__(self):
        return 'Pyscript error: {}'.format(self.err)


class IntervalError(Exception):
    def __str__(self):
        return 'Poorly matched BeginInterval-CompleteInterval'


class MainError(Exception):
    def __str__(self):
        return 'No "main" function defined'

def verbose_skip(func):
    def decorator(obj, *args, **kw):
        if obj._truncate:
            return

        fname = func.__name__
#        print fname, obj._syntax_checking, obj._cancel
        if fname.startswith('_m_'):
            fname = fname[3:]

        args1, _, _, defaults = inspect.getargspec(func)

        nd = sum([1 for di in defaults if di is not None]) if defaults else 0

        min_args = len(args1) - 1 - nd
        an = len(args) + len(kw)
        if an < min_args:
            raise PyscriptError('invalid arguments count for {}, args={} kwargs={}'.format(fname,
                                                                                           args, kw))
        if obj._syntax_checking or obj._cancel:
            return

        obj.debug('{} {} {}'.format(fname, args, kw))

        return func(obj, *args, **kw)
    return decorator

def skip(func):
    def decorator(obj, *args, **kw):
        if obj._syntax_checking or obj._cancel or obj._truncate:
            return
        return func(obj, *args, **kw)
    return decorator

def count_verbose_skip(func):
    def decorator(obj, *args, **kw):
        if obj._truncate:
            return

        fname = func.__name__
#        print fname, obj._syntax_checking, obj._cancel
        if fname.startswith('_m_'):
            fname = fname[3:]

        args1, _, _, defaults = inspect.getargspec(func)

        nd = sum([1 for di in defaults if di is not None]) if defaults else 0

        min_args = len(args1) - 1 - nd
        an = len(args) + len(kw)
        if an < min_args:
            raise PyscriptError('invalid arguments count for {}, args={} kwargs={}'.format(fname,
                                                                                           args, kw))
        if obj._syntax_checking or obj._cancel:
            func(obj, calc_time=True, *args, **kw)
            return

        obj.debug('{} {} {}'.format(fname, args, kw))

        return func(obj, *args, **kw)
    return decorator

def makeRegistry():
    registry = {}
    def registrar(func):
        registry[func.__name__] = func.__name__
        return func # normally a decorator returns a wrapped function, 
                    # but here we return func unmodified, after registering it
    registrar.commands = registry
    return registrar

def makeNamedRegistry(cmd_register):
    def named_register(name):
        def decorator(func):
            cmd_register.commands[name] = func.__name__
            return func
        return decorator

    return named_register

command_register = makeRegistry()
named_register = makeNamedRegistry(command_register)

class PyScript(Loggable):
    text = Property
    _text = Str

    manager = Any
    parent = Any
    root = Str
    filename = Str
    info_color = Str

    _ctx = Dict

    parent_script = Any

    _interval_stack = Queue
    _interval_flag = None

    _cancel = Bool(False)
    _completed = False
    _truncate = False

    syntax_checked = Property
    _syntax_checking = False
    _syntax_checked = False
    _gosub_script = None
    _wait_dialog = None

    cancel_flag = Bool
    hash_key = None
    info_display = DelegatesTo('manager')

    _estimated_duration = 0

    _graph_calc = False

    def check_for_modifications(self):
        old = self.toblob()
        with open(self.filename, 'r') as f:
            new = f.read()
        return old != new

    def toblob(self):
        return self.text

    def get_estimated_duration(self):
        return self._estimated_duration

    def setup_context(self, **kw):
        self._ctx.update(kw)

    def get_context(self):
        ctx = dict()
        for k  in self.get_commands():
            if isinstance(k, tuple):
                ka, kb = k
                name, func = ka, getattr(self, kb)
            else:
                name, func = k, getattr(self, k)

            ctx[name] = func

        for v in self.get_variables():
            ctx[v] = getattr(self, v)

        ctx.update(self._ctx)
        return ctx

    def get_variables(self):
        return []

    def get_core_commands(self):
        cmds = [
#                ('info', '_m_info')
                ]

        return cmds

    def get_commands(self):
        return self.get_core_commands() + \
                 self.get_script_commands() + \
                    self.get_command_register() + \
                        command_register.commands.items()

    def get_command_register(self):
        return []

    def get_script_commands(self):
        return []

    def truncate(self, style=None):
        if style is None:
            self._truncate = True

        if self._gosub_script is not None:
            self._gosub_script.truncate(style=style)

    def cancel(self):
        self._cancel = True
        if self._gosub_script is not None:
            if not self._gosub_script._cancel:
                self._gosub_script.cancel()

        if self.parent:
            self.parent._executing = False

        if self.parent_script:
            if not self.parent_script._cancel:
                self.parent_script.cancel()

        if self._wait_dialog:
            self._wait_dialog.close()

        self._cancel_hook()


    def bootstrap(self, load=True, **kw):
        self._interval_flag = Event()
        self._interval_stack = Queue()

        if self.root and self.name and load:
#            p = os.path.join(self.root, self.name)
#            self.syntax_checked = False
            with open(self.filename, 'r') as f:
                self.text = f.read()
            return True

#===============================================================================
# private
#===============================================================================
    def _cancel_hook(self):
        pass
    def _cancel_flag_changed(self, v):
        if v:
            result = confirmation(None, 'Are you sure you want to cancel {}'.format(self.logger_name))
            if result != 5104:
                self.cancel()
            else:
                self.cancel_flag = False
#==============================================================================
# commands
#==============================================================================
    @command_register
    def gosub(self, name=None, root=None, klass=None, **kw):
        if not name.endswith('.py'):
            name += '.py'

        if root is None:
            d = None
            if '/' in name:
                d = '/'
            elif ':' in name:
                d = ':'

            if d:
                dirs = name.split(d)
                name = dirs[0]
                for di in dirs[1:]:
                    name = os.path.join(name, di)

            root = self.root

        p = os.path.join(root, name)
        if not os.path.isfile(p):
            raise GosubError(p)

        if klass is None:
            klass = self.__class__
        else:
            klassname = klass
            pkg = 'src.pyscripts.api'
            mod = __import__(pkg, fromlist=[klass])
            klass = getattr(mod, klass)

        if not klass:
            raise KlassError(klassname)

        s = klass(root=root,
#                          path=p,
                          name=name,
                          _syntax_checked=self._syntax_checked,
                          manager=self.manager,
                          parent_script=self,
                          _ctx=self._ctx,
                          ** kw
                          )
#        s.bootstrap()

        if self._syntax_checking:
#            if not self.parent._syntax_checked:
#                self._syntax_checked = True
                s.bootstrap()
                err = s.test()
                if err:
                    raise PyscriptError(err)
        else:
            if not self._cancel:
                self.info('doing GOSUB')
                self._gosub_script = s
                s.execute()
                self._gosub_script = None
                if not self._cancel:
                    self.info('gosub finished')
    @verbose_skip
    @command_register
    def exit(self):
        self.info('doing EXIT')
        self.cancel()

#    @verbose_skip
#    @command_register
#    def wait(self, evt):
#        if evt is not None:
#            evt.wait()

    @command_register
    def complete_interval(self):
        try:
            pi = self._interval_stack.get(timeout=0.01)
            if pi != 'b':
                raise IntervalError()
        except Empty:
            raise IntervalError()

        if self._syntax_checking:
            return

        if self._cancel:
            return

        self.info('COMPLETE INTERVAL waiting for begin interval completion')
        #wait until _interval_flag is set
        while not self._interval_flag.isSet():
            if self._cancel:
                break
            self._sleep(0.5)

        if not self._cancel:
            self._interval_flag.clear()

    @verbose_skip
    @command_register
    def begin_interval(self, duration=0):
        def wait(t):
            self._sleep(t)
            if not self._cancel:
                self.info('interval finished')
                if self._interval_flag:
                    self._interval_flag.set()

        duration = float(duration)
#        if self._syntax_checking or self._cancel:
#            return
        self._interval_stack.put('b')

        self.info('BEGIN INTERVAL waiting for {}'.format(duration))
        t = Thread(target=wait, args=(duration,))
        t.start()

    @skip
    @named_register('info')
    def _m_info(self, message=None):
        message = str(message)
        self.info(message)

        try:
            if self.info_display:
                if self.info_color:
                    self.info_display.add_text(message, color=self.info_color)
                else:
                    self.info_display.add_text(message)

        except AttributeError:
            pass
#            do_later(self.info_display.add_text, message)

    @command_register
    def sleep(self, duration=0, message=None):
        self._estimated_duration += duration
        if self.parent_script is not None:
            self.parent_script._estimated_duration += self._estimated_duration

        if self._graph_calc:
            va = self._xs[-1] + duration
            self._xs.append(va)
            self._ys.append(self._ys[-1])
            return

        if self._syntax_checking or self._cancel:
            return

        self.info('SLEEP {}'.format(duration))
        if globalv.experiment_debug:
            duration = min(duration, 5)
        self._sleep(duration, message=message)

    def execute(self, new_thread=False, bootstrap=True, finished_callback=None):

        def _ex_():
            if bootstrap:
                self.bootstrap()

            ok = True
            if not self.syntax_checked:
                self.test()

            if ok:
                self._execute()
                if finished_callback:
                    finished_callback()

            return self._completed

        if new_thread:
            t = Thread(target=_ex_)
            t.start()
        else:
            return _ex_()

    def test(self):

        self._syntax_checking = True
        self.info('testing syntax')
        r = self._execute()

        if r is not None:
            self.info('invalid syntax')
            self.warning_dialog(str(r))
            raise PyscriptError(r)
#            report the traceback
#            self.info(r)

        elif not self._interval_stack.empty():
            raise IntervalError()

        else:
            self.info('syntax checking passed')

        self.syntax_checked = True
        self._syntax_checking = False

    def execute_snippet(self, snippet):
        safe_dict = self.get_context()
        try:
            code = compile(snippet, '<string>', 'exec')
            exec code in safe_dict
            safe_dict['main']()
        except KeyError:
            return MainError()

        except Exception, e:
            import traceback
            traceback.print_exc()
#            self.warning_dialog(str(e))
            return e
#            return  traceback.format_exc()

    def _execute(self):

        if not self.text:
            return 'No script text'

        self._cancel = False
        self._completed = False
        self._truncate = False

#        safe_dict['isblank'] = False
        error = self.execute_snippet(self.text)
        if error:
            return error

        if self._syntax_checking:
            return

#        self._post_execute_hook()

        if self._cancel:
            self.info('{} canceled'.format(self.name))
        else:
            self.info('{} completed successfully'.format(self.name))
            self._completed = True
            if self.parent:
                self.parent._executing = False
                try:
                    del self.parent.scripts[self.hash_key]
                except KeyError:
                    pass

#    def _post_execute_hook(self):
#        pass
#        if self.controller is not None:
#            self.controller.end()

    def _manager_action(self, func, name=None, protocol=None, *args, **kw):
#        man = self._get_manager()
        man = self.manager

        if protocol is not None and man is not None:
            app = man.application
            if app is not None:
                args = (protocol,)
                if name is not None:
                    args = (protocol, 'name=="{}"'.format(name))

                man = app.get_service(*args)

#        print man, manager, 'sadf'
        if man is not None:
            if not isinstance(func, list):
                func = [(func, args, kw)]

            return [getattr(man, f)(*a, **k) for f, a, k in func]
#            for f, a, k in func:
#                getattr(man, f)(*a, **k)
        else:
            self.warning('could not find manager {}'.format(name))
#    def _get_manager(self):
#        return self.manager

#==============================================================================
# Sleep/ Wait
#==============================================================================
    def _sleep(self, v, message=None):
        v = float(v)
#        if self._syntax_checking or self._cancel:
#            return

        if v > 1:
            if v >= 5:
                self._block(v, message=message, dialog=True)
            else:
                self._block(v, dialog=False)

        else:
            time.sleep(v)

    def _block(self, timeout, message=None, dialog=False):
        if dialog:
            if message is None:
                message = ''
            st = time.time()
#            c = Condition()
#            c.acquire()
            evt = Event()
            self._wait_dialog = wd = WaitDialog(wtime=timeout,
#                                condition=c,
                                end_evt=evt,
                                parent=self,
                                title='{} - Wait'.format(self.logger_name),
                                message='Waiting for {:0.1f}  {}'.format(timeout, message)
                                )

            do_later(wd.edit_traits)
            evt.wait(timeout=timeout + 1)
            do_later(wd.close)
            if wd._canceled:
                self.cancel()
            elif wd._continued:
                self.info('continuing script after {:0.3f} s'.format(time.time() - st))

        else:
            st = time.time()
            time.sleep(1)
            while time.time() - st < timeout:
                if self._cancel:
                    break
                time.sleep(1)

#===============================================================================
# properties
#===============================================================================
    @property
    def filename(self):
        return os.path.join(self.root, self.name)
    @property
    def state(self):
        #states
        #0=running
        #1=canceled
        #2=completed
        if self._cancel:
            return '1'

        if self._completed:
            return '2'

        return '0'

    def _get_text(self):
        return self._text

    def _set_text(self, t):
        self._text = t

    def _get_syntax_checked(self):
        return self._syntax_checked

    def _set_syntax_checked(self, v):
        self._syntax_checked = v

    def __str__(self):
        return self.name

if __name__ == '__main__':
    from src.helpers.logger_setup import logging_setup

    logging_setup('pscript')
#    execute_script(t)
    from src.paths import paths

    p = PyScript(root=os.path.join(paths.scripts_dir, 'pyscripts'),
                      path='test.py',
                      _manager=DummyManager())

    p.execute()
#============= EOF =============================================
