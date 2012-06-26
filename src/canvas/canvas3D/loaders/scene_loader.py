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



from src.canvas.canvas3D.loaders.scene_parser import SceneParser
'''
'''
#=============enthought library imports=======================

#=============standard library imports ========================
import os
import ConfigParser
#=============local library imports  ==========================
#from src.canvas.canvas3D.elements.components import *
from src.canvas.canvas3D.elements.components import Bone, Origin, PipetteValve, Shaft, \
    TextPanel, Valve, Bellows, SixWayCross, Turbo, Elbow, Flex, Sector, Quadrupole, Grid
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
    i = id_gen.next()
    if valid and canvas:
        canvas.valid_hitids.append(i)
    return i

def get_config(path):
    '''
    '''
    config = ConfigParser.ConfigParser()
    config.read(path)
    return config

def get_translation(elem):
    '''
    '''
    return get_floatlist(elem, 'translate')

def get_floatlist(elem, option):
    '''
    '''
    try:
        return [float(t) for t in
            elem.get(option).split(',')]
    except AttributeError:
        return []

def get_label_offset(elem):
    return get_floatlist(elem, 'label_offset')

class SceneLoader(object):
    '''
    '''

    delegations = None
    delegated_dependencies = []
    scene_graph = None
    def __init__(self, scene_graph):
        '''
        '''
        super(SceneLoader, self).__init__()
        self.delegated_dependencies = []
        self.delegations = []
        self._scene_graph = scene_graph

    def load_scene_graph(self, vm, canvas):
        '''
        '''
        sg = self._scene_graph

        sg.root = Node()
        t = Transform()
        sg.root.add(t)

        sp = SceneParser(os.path.join(paths.canvas3D_dir, 'extraction_line3D.xml'))
        self.load_view_elements(sp, t)
        self.load_bones(sp, sg, vm, canvas)
        self.load_spectrometers(sp, sg)
        self.load_six_way_cross(sp, sg)
        self.load_turbos(sp, sg)
        self.load_elbows(sp, sg)
        self.load_flexes(sp, sg)

        for p, o in self.delegations:
            p = sg.get_object_by_name(p)
            if p is not None:
                p.add(o)

        for obj, dependency in self.delegated_dependencies:
            if isinstance(obj, str):
                obj = sg.get_object_by_name(obj)
            dep = sg.get_object_by_name(dependency)
            obj.dependencies.append(dep)

    def load_view_elements(self, sp, transform):
        sg = self._scene_graph

        if sg.use_view_cube:
            vc = ViewCube(translate=(10, 10, 0))
            vc.id = 1
            sg.root.add(vc)

        show_origin = sp.get_show_origin()
        if show_origin:
            o = Origin()
            o.color = (0, 0, 1)
            transform.add(o)

#        show_grid = True
        show_grid = sp.get_show_grid()
        if show_grid:
            g = Grid()
            g.color = (1, 1, 0)
            transform.add(g)

    def load_bellows(self, section, sp, sg):
        '''
        '''
        for bi in sp.get_bellows(section):
            pname = bi.get('parent')
            if pname is None:
                pname = section.text.strip()

            self._factory(Bellows, bi, sg, pname)

    def load_six_way_cross(self, sp, sg):
        '''
        '''
        for si in sp.get_swcs():
            self._factory(SixWayCross, si, sg)

    def load_turbos(self, sp, sg):
        '''
        '''
        for pi in sp.get_turbos():
            self._factory(Turbo, pi, sg)

    def load_elbows(self, sp, sg):
        '''
        '''
        for ei in sp.get_elbows():
            self._factory(Elbow, ei, sg)

    def load_flexes(self, sp, sg):
        for fi in sp.get_flexes():
            f = self._factory(Flex, fi, sg)
            f.points = []
            for i, pt in enumerate(fi.findall('point')):
                f.points.append(map(float, pt.text.strip().split(',')))
                if i == 0:
                    f.points.append(map(float, pt.text.strip().split(',')))
            f.points.append(map(float, pt.text.strip().split(',')))

#    def load_info_panels(self, path, sg, vm, cv):
#        '''
#        '''
#        config = get_config(path)
#        for section in config.sections():
#            tx = TextPanel()
#            tx.id = new_id()
#            name = config.get(section, 'name')
#            tx.name = '{}_info_panel'.format(name)
#            tx.title = name
#            tx.translate = get_translation(config, section)
#            sg.root.add(tx)

    def load_spectrometers(self, sp, sg):
        '''
        '''
        klass = Sector
        gdict = globals()
        for mi in sp.get_spectrometers():
            klass = mi.get('klass')
            if klass is None:
                klass = Sector
            else:
                klass = gdict[klass]
            m = klass()
            m.id = new_id()
            m.name = mi.text.strip()
            m.translate = get_translation(mi)

            parent = mi.get('inlet')
            self._add_(sg, parent, m)

    def load_bones(self, sp, sg, vm, canvas):
        '''
        '''

        for section in sp.get_sections():
            b = Bone()
            b.id = new_id()
            b.name = section.text.strip()
            b.length = int(section.get('length'))
            b.translate = get_translation(section)

            sg.root[0].add(b)

            self.load_valves(section, sp, sg, vm, canvas)

            self.load_pipettes(section, b, sg)

            self.load_bellows(section, sp, sg)

    def load_pipettes(self, section, parent, sg):
        '''
        '''
        for pi in section.findall('pipette'):
            p = Bellows()
            p.id = new_id()

            p.name = 'pipette{}'.format(pi.text.strip())
            p.translate = get_translation(pi)
            p.radius = float(pi.get('radius'))

            self._add_(sg, parent, p)

            dep = pi.get('dependencies')
            p.dependencies = []
            if dep is not None:
                for di in dep.split(','):
                    self._add_dependencies(sg, p, di)

    def load_valves(self, section, sp, sg, vm, cv):
        '''
        '''
        gdict = globals()
        for velem in sp.get_valves(section):
            klass = velem.get('klass')
            if klass is None:
                klass = Valve
            else:
                klass = gdict[klass]

            v = klass()
            v.id = new_id(cv)
            v.canvas = cv
            v.valve_manager = vm
            v.name = velem.text.strip()
            v.translate = get_translation(velem)
            lo = get_label_offset(velem)
            if lo:
                v.label_offsets = lo

            parent = velem.get('parent')
            if parent is None:
                parent = section.text.strip()

            self._add_(sg, parent, v)

            if klass == Valve:
                self.load_valve_shafts(v, velem)

    def load_valve_shafts(self, valve, velem):
        '''
        '''

        shaft_gen = name_generator('shaft')
        b = Shaft()
        b.id = new_id()
        b.name = shaft_gen.next()

        shaft1, shaft2 = velem.findall('shaft')

        l = shaft1.get('length')
        if l is not None:
            b.length = float(l)

        angle = None
        shaft_or = shaft1.get('orientation')
        b.orientation = shaft_or

        leg = b.length / 2.0 - 1
        if shaft_or == 'down':
            if angle:
                b.translate = [0, 0, 0]
                b.rotate = [angle, 0, 0, 1]
            else:
                b.translate = [0, -leg, 0]

        elif shaft_or == 'forward':
            b.translate = [0, 0, -leg]
            b.rotate = [90, 1, 0, 0]
        elif shaft_or == 'backward':
            b.translate = [0, 0, leg]
            b.rotate = [-90, 1, 0, 0]

        arotate = shaft1.find('rotation')

        if arotate is not None:
            b.rotation_points = [(0, 0, leg), (0, -leg, 0)]
            b.rotate = [b.rotate, map(float, arotate.text.strip().split(','))]

        valve.add(b)
        valve.high_side = b

        bb = Shaft()
        bb.id = new_id()
        bb.name = shaft_gen.next()

        connector_or = shaft2.get('orientation')
        l = shaft2.get('length')
        if l is not None:
            bb.length = float(l)

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

        arotate2 = shaft2.find('rotation')
        if arotate2 is not None:
            bb.rotation_points = [(0, 0, leg), (0, -leg, 0)]
            bb.rotate = [bb.rotate, map(float, arotate2.text.strip().split(','))]

        valve.add(bb)
        valve.low_side = bb



    def _add_dependencies(self, sg, parent, dependencies):
        parent.dependencies = []
        for di in dependencies:
            do = sg.get_object_by_name(di)
            if do is None:
                self.delegated_dependencies.append((parent, di))
            else:
                parent.dependencies.append(do)

    def _add_(self, sg, pname, obj):
        if isinstance(pname, str):
            parent = sg.get_object_by_name(pname)
        else:
            parent = pname

        if parent is None:
            self.delegations.append((pname, obj))
        else:
            parent.add(obj)

    def _factory(self, klass, elem, sg, pname=None):
        obj = klass()
        obj.id = new_id()
        obj.name = elem.text.strip()
        obj.translate = get_translation(elem)


        obj.rotate = [map(float, rots.text.split(',')) for rots in elem.findall('rotation')]

        radius = elem.get('radius')
        if radius is not None:
            obj.radius = float(radius)

        if pname is None:
            pname = elem.get('parent')

        self._add_(sg, pname, obj)

        return obj

#================ EOF ==============================================
#        for name in rows:
##            name, _ending = r.split('.')
#            
#            loader = getattr(self, 'load_{}'.format(name))
##            loader = getattr(self, 'load_{}'.format(name[:-2]))
#            #loader(os.path.join(paths.canvas3D_dir, r), sg, vm, canvas)
#            loader(ip, sg, vm, canvas)
#

#    def load_connectors(self, path, sg, vm, canvas):
#        '''
#        '''
#
#        config = get_config(path)
#        for section in config.sections():
#            part = globals()[section]()
#            part.id = new_id()
#            part.name = config.get(section, 'name')
#            part.translate = get_translation(config, section)
#            part.rotate = [
#                         [float(t) for t in config.get(section, 'rot1').split(',')],
#                         [float(t) for t in config.get(section, 'rot2').split(',')]
#                        ]
#            parent = sg.get_object_by_name(config.get(section, 'parent'))
#
#            parent.add(part)
#            dep = config.get(section, 'dependencies').split(',')
#            for d in dep:
#                part.dependencies.append(sg.get_object_by_name(d))
#
#            if section == 'Flex':
#                #part.straight = False
#                fx, fy, fz = [float(v) for v in config.get(section, 'points').split(',')]
#                part.points = [(0, 0, 0), (0, 0, 0), (0, -1.5, 0),
#                      (fx, fy, fz + 1.5),
#                      (fx, fy, fz), (fx, fy, fz)
#                      ]
#
##                           ]
#
#    def load_connections(self, path, sg, vm, canvas):
#        '''
#
#        '''
#        config = get_config(path)
#        for section in config.sections():
#            v = sg.get_object_by_name(config.get(section, 'valve'))
#
#            connections = config.get(section, 'connections').split(',')
#            for c in connections:
#                v.connections.append(sg.get_object_by_name(c))
#
##        for args in connections:
##            v = sg.get_object_by_name(args[0])
##            for c in args[1:]:
##                p = sg.get_object_by_name(c)
##
##                v.connections.append(p)
##                


#
#    def part_factory(self, factory, name, translate, parentid, sg, dependencies=None, **kw):
#        '''
#        '''
#        p = factory(**kw)
#        p.id = new_id()
#        p.name = name
#        p.translate = translate
#
#        v = sg.get_object_by_name(parentid)
#        v.add(p)
#
#        if dependencies:
#            p.dependencies = dependencies
#
#        return p
#    def load_generic(self, path, sg, *args, **kw):
#        '''
#        '''
#        config = get_config(path)
#
#        for section in config.sections():
#            name = config.get(section, 'name')
#            translate = get_translation(config, section)
#            parent = config.get(section, 'parent')
#
#            dep = []
#            if config.has_option(section, 'dependencies'):
#                for n in config.get(section, 'dependencies').split(','):
#                    o = sg.get_object_by_name(n)
#                    if o is not None:
#                        dep.append(o)
#                    else:
#                        self.delegated_dependencies.append((name, n))
#
#
#            c = section.split('-')[0]
#            factory = globals()[c]
#
#            kw = {}
##            if config.has_option(section,'always_on'):
##                kw['always_on']=config.getboolean(section,'always_on')
#
#            if config.has_option(section, 'radius'):
#                kw['radius'] = config.getfloat(section, 'radius')
#            self.part_factory(factory, name, translate, parent, sg, dependencies=dep, **kw)

#    def load_sections(self,sg,vm):
#        
#        path=os.path.join(globalv.extraction_line_dir,'section_definitions.cfg')
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
