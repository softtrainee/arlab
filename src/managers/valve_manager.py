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
from traits.api import Any, Dict, List, Bool
#=============standard library imports ========================
import time
import os
import pickle
from pickle import PickleError
#=============local library imports  ==========================
from manager import Manager
from src.helpers.filetools import parse_setupfile
from src.helpers import paths
from src.extraction_line.explanation.explanable_item import ExplanableValve
from src.hardware.valve import HardwareValve
from src.extraction_line.section import Section
from src.helpers.paths import hidden_dir, setup_dir

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

        self.info('loading valve definitions file ')
        #open config file
        setup_file = os.path.join(paths.extraction_line_dir, 'valves.txt')
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

    def get_states(self):
        '''
        '''
        states = []
        for k, v in self.valves.items():
            states.append(k)
            if self.query_valve_state:
                s = self.get_state_by_name(k)
            else:
                s = v.state
            states.append('1' if s else '0')


        return ''.join(states)

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
            if self.query_valve_state:
                state = v.get_hardware_state()#actuator.get_channel_state(v)

            if state is None:
                state = v.state
            else:
                v.state = state

        return state

    def get_actuator_by_name(self, name):
        if self.actuators:
            for a in self.actuators:
                if a.name == name:
                    return a

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
        if address is None:
            v = self.get_valve_by_name(name)
            vid = name
        else:
            v = self.get_valve_by_address(address)
            vid = address

        result = None
        if v is not None:

            act = getattr(v, open_close)

            result = act(mode=mode)
            if isinstance(result, bool):#else its an error message

                ve = self.get_evalve_by_name(name)
                ve.state = True if open_close == 'open' else False

#                update the section state
#                for s in self.sections:
#                    s.update_state(action, v, self.valves, self.sample_gas_type, self.canvas3D.scene_graph)

                result = True

        else:
            self.warning('Valve %s not available' % vid)
            #result = 'Valve %s not available' % id

        return result

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
        ip = InitializationParser(os.path.join(setup_dir, 'initialization.xml'))

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
        c = parse_setupfile(path)

        self.sector_inlet_valve = c[0][0]
        self.quad_inlet_valve = c[0][1]

        actid = 5
        curgrp = None
        self.valve_groups = dict()

        for a in c[1:]:
            act = 'valve_controller'
            if len(a) == actid + 1:
                act = a[actid]

            name = a[0]
            actuator = self.get_actuator_by_name(act)
            warn_no_act = True
            if warn_no_act:
                if actuator is None:
                    self.warning_dialog('No actuator for {}. Valve will not operate. Check setupfiles/extractionline/valves.txt'.format(name))


            v = HardwareValve(name,
                     address=a[1],
                     actuator=self.get_actuator_by_name(act),
                     interlocks=a[2].split(','),
#                     group=a[4]
                     )
            try:
                if a[4] and a[4] != curgrp:
                    curgrp = a[4]
                    if self.valve_groups.has_key(curgrp):
                        self.valve_groups[curgrp].valves.append(v)
                    else:
                        vg = ValveGroup()
                        vg.valves = [v]
                        self.valve_groups[curgrp] = vg
                else:
                    self.valve_groups[curgrp].valves.append(v)

            except IndexError:

                #there is no group specified
                pass

            s = v.get_hardware_state()

            #update the extraction line managers canvas
#            self.parent.canvas.update_valve_state(v.name[-1], s)
            self.parent.update_valve_state(v.name[-1], s)
            args = dict(name=a[0],
                        address=a[1],
                        description=a[3],
                        canvas=self.parent.canvas,

                        )
            ev = ExplanableValve(**args)
            ev.state = s if s is not None else False

            self.valves[name] = v
            self.explanable_items.append(ev)

#        for k,g in self.valve_groups.iteritems():
#            
#            for v in g.valves:
#                print k,v.name
#==================== EOF ==================================

