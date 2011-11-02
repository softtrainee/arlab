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
'''
'''
#=============enthought library imports=======================

#=============standard library imports ========================
import os
import ConfigParser
#=============local library imports  ==========================
#from src.canvas.canvas3D.elements.components import *
from src.canvas.canvas3D.elements.components import Bone, Origin, PipetteValve, Shaft, \
    TextPanel, Valve, Bellows, SixWayCross, Turbo, Elbow, Flex, Sector, Quadrupole
from src.canvas.canvas3D.elements.node import Node
from src.canvas.canvas3D.elements.object3D import Transform
from src.helpers import paths
from src.helpers.filetools import parse_file
from src.canvas.canvas3D.canvases.tools.view_cube import ViewCube

def id_generator():
    '''
    '''
    i = 11
    while(1):
        yield(i)
        i += 1

id_gen = id_generator()

def name_generator(base):
    '''
    '''
    i = 0
    while(1):
        yield('{} {}'.format(base, i))
        i += 1

def new_id(canvas=None, valid=True):
    '''
    '''
    id = id_gen.next()
    if valid and canvas:
        canvas.valid_hitids.append(id)
    return id

def get_config(path):
    '''
    '''
    config = ConfigParser.ConfigParser()
    config.read(path)
    return config

def get_translation(config, section):
    '''
    '''
    return get_floatlist(config, section, 'translate')

def get_floatlist(config, section, option):
    '''
    '''
    return [float(t) for t in
            config.get(section, option).split(',')]

class SceneLoader(object):
    '''
    '''


    def __init__(self):
        '''
        '''
        super(SceneLoader, self).__init__()
        self.delegated_dependencies = []

    def load_scene_graph(self, sg, vm, canvas):
        '''
        '''

        pp = os.path.join(paths.canvas3D_dir, 'extractionline3D.txt')
        rows = parse_file(pp)
        if not rows:
            return

        sg.root = Node()
        t = Transform()
        sg.root.add(t)

        if sg.use_view_cube:
            vc = ViewCube(translate=(10, 10, 0))
            vc.id = 1
            sg.root.add(vc)

        show_origin = False
        if show_origin:
            o = Origin()
            o.color = (0, 0, 1)
            t.add(o)


        for r in rows:
            name, _ending = r.split('.')
            loader = getattr(self, 'load_{}'.format(name[:-2]))
            loader(os.path.join(paths.canvas3D_dir, r), sg, vm, canvas)

        for obj, dependency in self.delegated_dependencies:
            obj = sg.get_object_by_name(obj)
            dep = sg.get_object_by_name(dependency)
            obj.dependencies.append(dep)


#    def load_sections(self,sg,vm):
#        
#        path=os.path.join(globals.extraction_line_dir,'section_definitions.cfg')
#        config=get_config(path)
#
#        for section in config.sections():
#            s=Section()
#            s.name=section.split('-')[1]
#            s.valve_manager=vm
#            s.scene_graph=sg
#            if config.has_option(section,'precedence'):
#                s.precedence=config.getint(section, 'precedence')
#            #s.name=config.get(section,'name')
#            s.components=[c for c in config.get(section,'components').split(',')]
#            for o in config.options(section):
#                
#                if 'test' in o:
#                    t=config.get(section, o)
#                    vname=t.split('-')[0]
#                    s.add_test(t)
#                    
#                    v=sg.get_object_by_name(vname)
#                    v.add_section(s)
#        



    def load_connectors(self, path, sg, vm, canvas):
        '''
            @type path: C{str}
            @param path:

            @type sg: C{str}
            @param sg:

            @type vm: C{str}
            @param vm:

            @type canvas: C{str}
            @param canvas:
        '''

        config = get_config(path)
        for section in config.sections():
            part = globals()[section]()
            part.id = new_id()
            part.name = config.get(section, 'name')
            part.translate = get_translation(config, section)
            part.rotate = [
                         [float(t) for t in config.get(section, 'rot1').split(',')],
                         [float(t) for t in config.get(section, 'rot2').split(',')]
                        ]
            parent = sg.get_object_by_name(config.get(section, 'parent'))

            parent.add(part)
            dep = config.get(section, 'dependencies').split(',')
            for d in dep:
                part.dependencies.append(sg.get_object_by_name(d))
            if section == 'Flex':
                #part.straight = False
                fx, fy, fz = [float(v) for v in config.get(section, 'points').split(',')]
                part.points = [(0, 0, 0), (0, 0, 0), (0, -1.5, 0),
                      (fx, fy, fz + 1.5),
                      (fx, fy, fz), (fx, fy, fz)
                      ]

#                           ]

    def load_connections(self, path, sg, vm, canvas):
        '''

        '''
        config = get_config(path)
        for section in config.sections():
            v = sg.get_object_by_name(config.get(section, 'valve'))

            connections = config.get(section, 'connections').split(',')
            for c in connections:
                v.connections.append(sg.get_object_by_name(c))

#        for args in connections:
#            v = sg.get_object_by_name(args[0])
#            for c in args[1:]:
#                p = sg.get_object_by_name(c)
#
#                v.connections.append(p)
#                

    def load_bellows(self, path, sg, vm, canvas):
        '''
        '''
        self.load_generic(path, sg)


    def load_six_way_cross(self, path, sg, vm, canvas):
        '''
        '''

        self.load_generic(path, sg)

    def load_pumps(self, path, sg, vm, canvas):
        '''
        '''
        def additional_turbo_args(section, config):

            rdict = {}
            if config.has_option(section, 'always_on'):
                rdict['always_on'] = config.getboolean(section, 'always_on')
            return rdict

        self.load_generic(path, sg)



    def load_info_panels(self, path, sg, vm, cv):
        '''
        '''
        config = get_config(path)
        for section in config.sections():
            tx = TextPanel()
            tx.id = new_id()
            name = config.get(section, 'name')
            tx.name = '{}_info_panel'.format(name)
            tx.title = name
            tx.translate = get_translation(config, section)
            sg.root.add(tx)

    def load_mass_specs(self, path, sg, vm, cv):
        '''
        '''
        config = get_config(path)
        for section in config.sections():
            spec = globals()[section.split('-')[0]]()
            spec.id = new_id()
            spec.name = config.get(section, 'name')
            spec.translate = get_translation(config, section)
            parent = config.get(section, 'parent')
            spec.parent = parent
            v = sg.get_object_by_name(parent)

            spec.inlet = v
            v.add(spec)


    def load_bones(self, path, sg, vm, canvas):
        '''
        '''
        config = get_config(path)

        for section in config.sections():
            b = Bone()
            b.id = new_id()
            b.name = config.get(section, 'name')
            b.length = config.getint(section, 'length')
            b.translate = get_translation(config, section)

            sg.root[0].add(b)

    def load_outer_pipette_valves(self, *args, **kw):
        '''

        '''
        self._load_pipette_valves(*args, **kw)

    def load_inner_pipette_valves(self, *args, **kw):
        '''
        '''
        self._load_pipette_valves(*args, **kw)

    def _load_pipette_valves(self, *args, **kw):
        '''
        '''
        args += (PipetteValve,)
        self._load_valves(*args, **kw)

    def load_pipettes(self, *args, **kw):
        '''
        '''
        self.load_generic(*args, **kw)

    def load_valves(self, *args, **kw):
        '''
        '''
        args += (Valve,)
        self._load_valves(*args, **kw)

    def _load_valves(self, path, sg, vm, cv, _valve_class_):
        '''
        '''

        config = get_config(path)
        for section in config.sections():

            v = _valve_class_()
            v.id = new_id(cv)
            v.canvas = cv
            v.valve_manager = vm

            v.name = config.get(section, 'name')
            v.translate = get_translation(config, section)
            v.label_offsets = get_floatlist(config, section, 'labeloffset')
            option = None
            if config.has_option(section, 'group'):
                option = 'group'
            elif config.has_option(section, 'parent'):
                option = 'parent'

            if option:
                p = sg.get_object_by_name(config.get(section, option))
                if p:
                    p.add(v)
            else:
                #add to the scenes Transform
                sg.root[0].add(v)
#            if isinstance(p,Bone):
#                p.dependencies.append(v)

            if _valve_class_ == Valve:
                self.load_valve_shafts(v, config, section)

    def load_valve_shafts(self, valve, config, section):
        '''
        '''

        shaft_gen = name_generator('shaft')
        b = Shaft()
        b.id = new_id()
        b.name = shaft_gen.next()

        shaft_or = config.get(section, 'shaft1')

        if config.has_option(section, 'shaft1_length'):
            b.length = config.getint(section, 'shaft1_length')

        angle = None

        b.orientation = shaft_or

        leg = b.length / 2.0 - 1
        if shaft_or == 'down':
            if angle:
                b.translate = [0, 0, 0]
                b.rotate = [angle, 0, 0, 1]
            else:


                b.translate = [0, -leg, 0]
#                b.translate = [0, -2, 0]

        elif shaft_or == 'forward':
            b.translate = [0, 0, -leg]
            b.rotate = [90, 1, 0, 0]
        elif shaft_or == 'backward':
            b.translate = [0, 0, leg]
            b.rotate = [-90, 1, 0, 0]


        valve.add(b)
        valve.low_side = b
        #valve.shaft1=b

        bb = Shaft()
        bb.id = new_id()
        bb.name = shaft_gen.next()
        connector_or = config.get(section, 'shaft2')

        if config.has_option(section, 'shaft2_length'):
            bb.length = config.getint(section, 'shaft2_length')
        leg = bb.length / 2.0 - 1

        bb.orientation = connector_or
        if connector_or == 'backward':
            bb.rotate = [90, 1, 0, 0]
        elif connector_or == 'forward':
            bb.rotate = [-90, 1, 0, 0]
        elif connector_or == 'left':
            bb.rotate = [-90, 0, 0, 1]
        elif connector_or == 'right':
            bb.rotate = [90, 0, 0, 1]
        elif connector_or == 'down':
            bb.translate = [0, -leg, 0]
        #valve.shaft2=bb
        valve.add(bb)
        valve.high_side = bb

    def part_factory(self, factory, name, translate, parentid, sg, dependencies=None, **kw):
        '''
        '''
        p = factory(**kw)
        p.id = new_id()
        p.name = name
        p.translate = translate

        v = sg.get_object_by_name(parentid)
        v.add(p)

        if dependencies:
            p.dependencies = dependencies

        return p

    def load_generic(self, path, sg, *args, **kw):
        '''
        '''
        config = get_config(path)

        for section in config.sections():
            name = config.get(section, 'name')
            translate = get_translation(config, section)
            parent = config.get(section, 'parent')

            dep = []
            if config.has_option(section, 'dependencies'):
                for n in config.get(section, 'dependencies').split(','):
                    o = sg.get_object_by_name(n)
                    if o is not None:
                        dep.append(o)
                    else:
                        self.delegated_dependencies.append((name, n))


            c = section.split('-')[0]
            factory = globals()[c]

            kw = {}
#            if config.has_option(section,'always_on'):
#                kw['always_on']=config.getboolean(section,'always_on')

            if config.has_option(section, 'radius'):
                kw['radius'] = config.getfloat(section, 'radius')
            self.part_factory(factory, name, translate, parent, sg, dependencies=dep, **kw)



#================ EOF ===============
#def _generic_(self, factory, sg, args):
#        '''
#            @type factory: C{str}
#            @param factory:
#
#            @type sg: C{str}
#            @param sg:
#
#            @type args: C{str}
#            @param args:
#        '''
#        g = factory()
#        g.id = new_id()
#        g.name = args[0]
#        g.translate = [float(v) for v in args[1:4]]
#
#        
#        v = sg.get_object_by_name(args[4])
#        v.add(g)
#        return g
#   def load_connectors(self, connectors, sg, vm, canvas):
#        '''
#            @type connectors: C{str}
#            @param connectors:
#
#            @type sg: C{str}
#            @param sg:
#
#            @type vm: C{str}
#            @param vm:
#
#            @type canvas: C{str}
#            @param canvas:
#        '''
#        for args in connectors:
#            type = args[0]
#
#            if type == 'elbow':
#                f = Elbow
#            else:
#                f = Bellows
#
#
#            part = f()
#            part.id = new_id()
#            part.name = args[1]
#            part.translate = [float(v) for v in args[2:5]]
#
#            part.rotate = [
#                         [float(v) for v in args[5:9]],
#                         [float(v) for v in args[9:13]]
#                         ]
#
#            parent = sg.get_object_by_name(args[13])
#
#            parent.add(part)
#
#            if len(args) >= 15:
#                for d in args[14]:
#
#                    di = sg.get_object_by_name(d)
#                    part.dependencies.append(di)
#
#                if type == 'flex':
#                    part.straight = False
#                    fx, fy, fz = [float(v) for v in args[15:18]]
#                    part.points = [(0, 0, 0), (0, 0, 0), (0, -1.5, 0),
#                          (fx, fy, fz + 1.5),
#                          (fx, fy, fz), (fx, fy, fz)
#
#       j=valves.index('<G>')
#        j = 0
#        for i, x in enumerate(valves):
#            if '<G>' in x:
#                j = i
#                break
#
#        valvelist = [('bone', valves[:j]), ('minibone', valves[j + 1:])]
#
#        
#        
#        for b, valves in valvelist:
#            bone = sg.get_object_by_name(b)
#            for vattr in valves:
#                valve = Valve()
#
#                #vattr=v.split(',')
#                valve.name = vattr[0]
#                valve.translate = [float(vi) for vi in vattr[1:4]]
#                valve.id = new_id(cv)
#                valve.label_offsets = [float(vi) for vi in vattr[6:8]]
#                valve.valve_manager = vm
#                valve.canvas = cv
#
#                bone.add(valve)
#                bone.dependencies.append(valve)
#
#                self.load_valve_shafts(valve, vattr)
