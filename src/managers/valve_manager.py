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

#=============enthought library imports=======================
from traits.api import Any, Dict, List, Bool
#=============standard library imports ========================
import os
import pickle
from pickle import PickleError
#=============local library imports  ==========================
from manager import Manager
from src.helpers import paths
from src.extraction_line.explanation.explanable_item import ExplanableValve
from src.hardware.valve import HardwareValve
from src.extraction_line.section import Section
from src.helpers.paths import hidden_dir
from src.helpers.valve_parser import ValveParser
from threading import Timer, Thread, Condition, Event
import time
from src.loggable import Loggable
import random
from Queue import Queue
from src.hardware.actuators.argus_gp_actuator import ArgusGPActuator
from globals import ignore_initialization_warnings


class ValveGroup(object):
    owner = None
    valves = None


class ValveManager(Manager):
    '''
    Manager to interface with the UHV and HV pneumatic valves
    
    '''
    valves = Dict
    explanable_items = List
    #parent = Any
    sampletime = 0.1
    #actuator = Any
    actuators = List
    canvas3D = Any
    sections = List

    sample_gas_type = None #valid values None,sample,air
    sector_inlet_valve = None
    quad_inlet_valve = None

    query_valve_state = Bool(True)

    systems = None
    valve_groups = None

    def show_valve_properties(self, name):
        v = self.get_valve_by_name(name)
        if v is not None:
            v.edit_traits()

    def kill(self):
        super(ValveManager, self).kill()
        self.save_soft_lock_state()

    def create_device(self, name, *args, **kw):
        '''
        '''
        dev = Manager.create_device(self, name, *args, **kw)
        if 'actuator' in name or 'controller' in name:
            if dev is not None:
                self.actuators.append(dev)
#        if name in ['valve_actuator', 'valve_controller']:
#            self.actuator = dev
            return dev

    def finish_loading(self, update=False):
        '''
   
        '''
        if self.actuators:
            for a in self.actuators:
                self.info('setting actuator {}'.format(a.name))

                self.info('comm. device = {} '.format(a._cdevice.__class__.__name__))

        #open config file
        setup_file = os.path.join(paths.extraction_line_dir, 'valves.xml')
        self._load_valves_from_file(setup_file)

        self.load_soft_lock_state()

        self._load_system_dict()
        #self.info('loading section definitions file')
        #open config file
        #setup_file = os.path.join(paths.extraction_line_dir, 'section_definitions.cfg')
        #self._load_sections_from_file(setup_file)
    def save_soft_lock_state(self):

        p = os.path.join(hidden_dir, 'soft_lock_state')
        self.info('saving soft lock state to {}'.format(p))
        with open(p, 'wb') as f:
            obj = dict([(k, v.software_lock) for k, v in self.valves.iteritems()])

            pickle.dump(obj, f)

    def load_soft_lock_state(self):
        p = os.path.join(hidden_dir, 'soft_lock_state')
        if os.path.isfile(p):
            self.info('loading soft lock state from {}'.format(p))

            with open(p, 'rb') as f:
                try:
                    sls = pickle.load(f)
                except PickleError:
                    pass

                for v in self.valves:

                    if v in sls and sls[v]:
                        self.lock(v, save=False)
                    else:
                        self.unlock(v, save=False)

    def get_software_locks(self):
        locks = []
        for k, v in self.valves.items():
            locks.append(k)
            locks.append('1' if v.software_lock else '0')

#            if self.query_valve_state:
#                s = self.get_state_by_name(k)
#            else:
#                s = v.state

        return ''.join(locks)

    def _get_states(self, times_up_event, sq):

        def _gstate(ki):
            sq.put(ki)
            s = self.get_state_by_name(ki)
            sq.put('1' if s else '0')

        dv = []
        for k, v in self.valves.iteritems():
#        for k, _ in self.valves.items():
            if v.query_state:
                dv.append(k)
                continue

            if times_up_event.isSet():
                break

            _gstate(k)

        if times_up_event.isSet():
            return

        for k in dv:
            if times_up_event.isSet():
                break
            _gstate(k)

    def get_states(self, timeout=1):
        '''
            use event and timer to allow for partial responses
            the timer t will set the event in timeout seconds

            after the timer is started _get_states is called
            _get_states loops thru the valves querying their state

            each iteration the times_up_event is checked to see it
            has fired if it has the the loop breaks and returns the
            states word
        
            to prevent the communicator from blocking longer then the times up event
            the _gs_thread is joined and timeouts out after 1.01s 
        '''

        states_queue = Queue()
        times_up_event = Event()
        t = Timer(1, lambda: times_up_event.set())
        t.start()
        try:

            _gs_thread = Thread(name='valves.get_states',
                                target=self._get_states, args=(times_up_event, states_queue))
            _gs_thread.start()
            _gs_thread.join(timeout=1.01)
        except (Exception,), e:
            pass

        #ensure word has even number of elements
        s = ''
        i = 0
        n = states_queue.qsize()
        if n % 2 != 0:
            c = n / 2 * 2
        else:
            c = n

        while not states_queue.empty() and i < c:
            s += states_queue.get_nowait()
            i += 1

        return s

    def get_valve_by_address(self, a):
        '''
        '''
        return next((valve for valve in self.valves.itervalues() if valve.address == a), None)

    def get_name_by_address(self, k):
        '''
        '''
        v = self.get_valve_by_address(k)
        if v is not None:
            return v.name

    def get_valve_by_name(self, n):
        '''    
        '''
        if n in self.valves:
            return self.valves[n]

    def get_evalve_by_name(self, n):
        '''  
        '''
        return next((item for item in self.explanable_items if item.name == n), None)

    def get_state_by_name(self, n):
        '''
        '''
        v = self.get_valve_by_name(n)
        state = None
        if v is not None:
            if self.query_valve_state and v.query_state:
                state = v.get_hardware_state()#actuator.get_channel_state(v)

            if state is None:
                state = v.state
            else:
                v.state = state

        return state

    def get_actuator_by_name(self, name):
        if self.actuators:
#            for a in self.actuators:
#                if a.name == name:
#                    return a
            return next((a for a in self.actuators if a.name == name), None)

    def get_software_lock(self, name):
        v = self.get_valve_by_name(name)

        if v is not None:
            return v.software_lock

    def claim_section(self, section, addr=None, name=None):
        try:
            vg = self.valve_groups[section]
        except KeyError:
            return True

        if addr is None:
            addr = self._get_system_address(name)

        vg.owner = addr

    def release_section(self, section):
        try:
            vg = self.valve_groups[section]
        except KeyError:
            return True

        vg.owner = None

    def get_system(self, addr):
        return next((k for k, v in self.systems.iteritems() if v == addr), None)

    def check_group_ownership(self, name, claimer):
        grp = None
        for g in self.valve_groups.itervalues():
            for vi in g.valves:
                if vi.is_name(name):
                    grp = g
                    break
        r = False
        if grp is not None:
            r = grp.owner == claimer

#        print name, claimer,grp, r
        return r

#    def check_ownership(self, name, sender_address):
#        v = self.get_valve_by_name(name)
#        
#        system = self.get_system(sender_address)
#        
#        if v is not None:
#            if v.system == system:
#                return True


    def check_soft_interlocks(self, name):
        ''' 
        '''
        cv = self.get_valve_by_name(name)

        if cv is not None:
            interlocks = cv.interlocks
            valves = self.valves
            for v in valves:

                if valves[v].name in interlocks:
                    if valves[v].state:
                        return True

    def open_by_name(self, name, mode='normal'):
        '''
        '''
        return self._open_(name, mode)

    def close_by_name(self, name, mode='normal'):
        '''
        '''
        return self._close_(name, mode)

    #@recordable
    def _actuate_(self, name, open_close, mode, address=None):
        '''
        '''
        change = False
        if address is None:
            v = self.get_valve_by_name(name)
            vid = name
        else:
            v = self.get_valve_by_address(address)
            vid = address

        result = None
        if v is not None:

            act = getattr(v, open_close)

            result, change = act(mode=mode)
            if isinstance(result, bool):#else its an error message
                if result:
                    ve = self.get_evalve_by_name(name)
                    ve.state = True if open_close == 'open' else False

#                update the section state
#                for s in self.sections:
#                    s.update_state(action, v, self.valves, self.sample_gas_type, self.canvas3D.scene_graph)

                #result = True

        else:
            self.warning('Valve %s not available' % vid)
            #result = 'Valve %s not available' % id

        return result, change

    def sample(self, name, period):
        v = self.get_valve_by_name(name)
        if v and not v.state:
            self.info('start sample')
            self.open_by_name(name)

#            time.sleep(period)
#
#            self.info('end sample')
#            self.close_by_name(name)
#    def sample(self, vid, parent):
#        '''
#
#        '''
#        #do not sample a open valve
#        # fixme 
#        #span a new thread to perform the the sampling
#        v = self.get_valve_by_name(vid)
#        if self.validate(v) and not v.state:
#
#            parent.open(v.name)
#            parent.update()
#
#            self.info('start sampling')
#            time.sleep(self.sampletime)
#
#            parent.close(v.name)
#            parent.update()
#
#            self.info('end sampling')

    def lock(self, name, save=True):
        '''
        '''
        v = self.get_valve_by_name(name)
        if v is not None:
            ev = self.get_evalve_by_name(name)
            if ev is not None:
                ev.soft_lock = True
            v.lock()
            if save:
                self.save_soft_lock_state()

    def unlock(self, name, save=True):
        '''
        '''
        v = self.get_valve_by_name(name)
        if v is not None:
            ev = self.get_evalve_by_name(name)
            if ev is not None:
                ev.soft_lock = False
            v.unlock()
            if save:
                self.save_soft_lock_state()


    def validate(self, v):
        '''
        return false if v's interlock valve(s) is(are) open
        else return true
        '''

        return next((False for vi in v.interlocks if self.get_valve_by_name(vi).state), True)

#        #check interlock conditions
#        for i in v.interlocks:
#            t = self.get_valve_by_name(i)
#            if t.state:
#                return False
#        else:
#            return True

    def _open_(self, name, mode):
        '''
        '''
        open_close = 'open'
        #check software interlocks and return None if True
        if self.check_soft_interlocks(name):
            self.warning('Software Interlock')
            return

        return self._actuate_(name, open_close, mode)

    def _close_(self, name, mode):
        '''
        '''
        open_close = 'close'
        if self.check_soft_interlocks(name):
            self.warning('Software Interlock')
            return

        return self._actuate_(name, open_close, mode)

    def _get_system_address(self, name):
        return next((h for k, h in self.systems.iteritems() if k == name), None)

    def _load_system_dict(self):
#        config = self.configparser_factory()

        from src.helpers.initialization_parser import InitializationParser
#        ip = InitializationParser(os.path.join(setup_dir, 'initialization.xml'))
        ip = InitializationParser()

        self.systems = dict()
        for name, host in ip.get_systems():
            self.systems[name] = host

#        config.read(os.path.join(setup_dir, 'system_locks.cfg'))
#        
#        for sect in config.sections():
#            name = config.get(sect, 'name')
#            host = config.get(sect, 'host')
##            names.append(name)
#            self.systems[name] = host
#    
    def _load_sections_from_file(self, path):
        '''
        '''
        self.sections = []
        config = self.get_configuration(path=path)
        if config is not None:
            for s in config.sections():
                section = Section()
                comps = config.get(s, 'components')
                for c in comps.split(','):
                    section.add_component(c)

                for option in config.options(s):
                    if 'test' in option:
                        test = config.get(s, option)
                        tkey, prec, teststr = test.split(',')
                        t = (int(prec), teststr)
                        section.add_test(tkey, t)

                self.sections.append(section)

    def _load_valves_from_file(self, path):
        '''
        '''
        self.info('loading valve definitions file  {}'.format(path))
        def factory(v):
            name, hv = self._valve_factory(v)
            self._load_explanation_valve(hv)
            self.valves[name] = hv
            return hv

        self.valve_groups = dict()
        parser = ValveParser(path)
        for g in parser.get_groups():
            valves = [factory(v) for v in parser.get_valves(group=g)]
            vg = ValveGroup()
            vg.valves = valves
            self.valve_groups[g.text.strip()] = vg

        for v in parser.get_valves():
            factory(v)

    def _valve_factory(self, v_elem):
        name = v_elem.text.strip()
        address = v_elem.find('address')
        act_elem = v_elem.find('actuator')
        description = v_elem.find('description')
        interlocks = [i.text.strip() for i in v_elem.findall('interlock')]
        if description is not None:
            description = description.text.strip()

        actname = act_elem.text.strip() if act_elem is not None else 'valve_controller'
        actuator = self.get_actuator_by_name(actname)
        if actuator is None:
            if not ignore_initialization_warnings:
                self.warning_dialog('No actuator for {}. Valve will not operate. Check setupfiles/extractionline/valves.xml'.format(name))

        qs = True
        vqs = v_elem.get('query_state')
        if vqs:
            qs = vqs == 'true'
        hv = HardwareValve(name,
                           address=address.text.strip() if address is not None else '',
                           actuator=actuator,
                           description=description,
                           query_state=qs,
                           interlocks=interlocks
                           )
        return name, hv

    def _load_explanation_valve(self, v):
        s = v.get_hardware_state()
        #update the extraction line managers canvas
#            self.parent.canvas.update_valve_state(v.name[-1], s)
        name = v.name.split('-')[1]
        self.parent.update_valve_state(name, s)
#        args = dict(
#                    )
        ev = ExplanableValve(name=name,
                    address=v.address,
                    description=v.description,
                    canvas=self.parent.canvas,)
        ev.state = s if s is not None else False

        self.explanable_items.append(ev)


class Foo(Loggable):
    def get_state_by_name(self, m):
        b = random.randint(1, 5) / 50.0
        r = 0.1 + b
#        r = 3
        self.info('sleep {}'.format(r))
        time.sleep(r)
        return True

    def _get_states(self, times_up_event, sq):
#        self.states = []
        for k in ['A', 'B', 'Ca', 'Dn', 'Es', 'F', 'G', 'H', 'I']:
            if times_up_event.isSet():
                break

            sq.put(k)
#            self.info('geting state for {}'.format(k))
            s = self.get_state_by_name(k)
#            self.info('got {} for {}'.format(s, k))
            if times_up_event.isSet():
                break
            sq.put('1' if s else '0')

        #return ''.join(states)

    def get_states(self):
        '''
            with this method you need to ensure the communicators timeout
            is sufficiently low. the communicator will block until a response
            or a timeout. the times up event only breaks between state queries.
        
        '''
        states_queue = Queue()
        times_up_event = Event()
        t = Timer(1, lambda: times_up_event.set())
        t.start()
#        states = self._get_states(times_up_event)
#        return states
        t = Thread(target=self._get_states, args=(times_up_event, states_queue))
        t.start()
        t.join(timeout=1.1)
        s = ''

        n = states_queue.qsize()
        if n % 2 != 0:
            c = n / 2 * 2
        else:
            c = n

        i = 0
        while not states_queue.empty() and i < c:
            s += states_queue.get_nowait()
            i += 1

#        n = len(s)
#        if n % 2 != 0:
#            sn = s[:n / 2 * 2]
#        else:
#            sn = s
#        s = ''.join(self.states)
        self.info('states = {}'.format(s))
        return s

if __name__ == '__main__':
#    v = ValveManager()
#    p = os.path.join(paths.extraction_line_dir, 'valves.xml')
#    v._load_valves_from_file(p)
    from src.helpers.logger_setup import logging_setup

    logging_setup('foo')
    f = Foo()
    for i in range(10):
        r = f.get_states()
        time.sleep(2)
        #print r, len(r)

#==================== EOF ==================================
#def _load_valves_from_filetxt(self, path):
#        '''
#
#        '''
#        c = parse_setupfile(path)
#
#        self.sector_inlet_valve = c[0][0]
#        self.quad_inlet_valve = c[0][1]
#
#        actid = 6
#        curgrp = None
#        self.valve_groups = dict()
#
#        for a in c[1:]:
#            act = 'valve_controller'
#            if len(a) == actid + 1:
#                act = a[actid]
#
#            name = a[0]
#            actuator = self.get_actuator_by_name(act)
#            warn_no_act = True
#            if warn_no_act:
#                if actuator is None:
#                    self.warning_dialog('No actuator for {}. Valve will not operate. Check setupfiles/extractionline/valves.txt'.format(name))
#            print a
#            v = HardwareValve(name,
#                     address=a[1],
#                     actuator=self.get_actuator_by_name(act),
#                     interlocks=a[2].split(','),
#                     query_valve_state=a[4] in ['True', 'true']
##                     group=a[4]
#                     )
#            try:
#                if a[5] and a[5] != curgrp:
#                    curgrp = a[5]
#                    if curgrp in self.valve_groups:
#                        self.valve_groups[curgrp].valves.append(v)
#                    else:
#                        vg = ValveGroup()
#                        vg.valves = [v]
#                        self.valve_groups[curgrp] = vg
#                else:
#                    self.valve_groups[curgrp].valves.append(v)
#
#            except IndexError:
#
#                #there is no group specified
#                pass
#
#            s = v.get_hardware_state()
#
#            #update the extraction line managers canvas
##            self.parent.canvas.update_valve_state(v.name[-1], s)
#            self.parent.update_valve_state(v.name[-1], s)
#            args = dict(name=a[0],
#                        address=a[1],
#                        description=a[3],
#                        canvas=self.parent.canvas,
#
#                        )
#            ev = ExplanableValve(**args)
#            ev.state = s if s is not None else False
#
#            self.valves[name] = v
#            self.explanable_items.append(ev)

#        for k,g in self.valve_groups.iteritems():
#            
#            for v in g.valves:
#                print k,v.name
