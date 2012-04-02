#!/usr/bin/python
# -*- coding: utf-8 -*-

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
#============= enthought library imports  ==========================
from traits.api import HasTraits, Instance, \
    Float, Str, List
from traitsui.api import View, Item, HGroup, HSplit, VGroup, spring, \
    ListEditor
#============= standard library imports  ==========================
#============= local library imports  ==========================
from src.graph.graph import Graph


class BakeoutParameters(HasTraits):
    setpoint = Float
    duration = Float
    max_output = Float
    script = Str
    name = Str
    script_text = Str
    view = View(
               Item('duration', style='readonly'),
               Item('setpoint', style='readonly'),
               Item('max_output', style='readonly'),
               Item('script', style='readonly'),
               Item('script_text', show_label=False, style='custom',
                    enabled_when='0')
                               )


class BakeoutGraphViewer(HasTraits):
    graph = Instance(Graph)
    bakeouts = List
    title = Str
    window_x = Float
    window_y = Float
    window_width = Float
    window_height = Float

    def new_controller(self, name):
        bc = BakeoutParameters(name=name)
        self.bakeouts.append(bc)
        return bc

    def traits_view(self):
        bakeout_group = Item('bakeouts', style='custom',
                             show_label=False,
                             editor=ListEditor(use_notebook=True,
                                                           dock_style='tab',
                                                           page_name='.name'
                                                           ))
        v = View(HSplit(Item('graph', style='custom', show_label=False),
                        bakeout_group
                        ),
                 resizable=True,
                 title=self.title,
                 x=self.window_x,
                 y=self.window_y,
                 width=self.window_width,
                 height=self.window_height
                 )
        return v

# ============= EOF ====================================
