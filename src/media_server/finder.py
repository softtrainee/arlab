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
from traits.api import HasTraits, Str, List, Instance
from traitsui.api import View, Item, TableEditor
from traitsui.tree_node import TreeNode, ITreeNode
from traitsui.editors.tree_editor import TreeEditor
#============= standard library imports ========================
#============= local library imports  ==========================
class FilePath(HasTraits):
    name = Str

class Hierarchy(HasTraits):
    name = Str
    children = List

class Finder(HasTraits):
    hierarchy = Instance(Hierarchy)
    def traits_view(self):
        def foo(*args, **kw):
            print 'acaiasdf', args, kw
        nodes = [TreeNode(node_for=[Hierarchy],
                          children='children',
                          label='name',
                          on_activated=foo
                          ),
                 TreeNode(node_for=[FilePath],
                          label='name',
                          on_activated=foo
                          )
                 ]
        v = View(Item('hierarchy',
                      show_label=False,
                      editor=TreeEditor(nodes=nodes)),
                 resizable=True,
                 width=500,
                 height=500
                 )
        return v

if __name__ == '__main__':
    f = Finder()
    hs = [Hierarchy(name='moo{}'.format(i)) for i in range(3)]
    for j, hi in enumerate(hs):
        hi.children = [FilePath(name='foo{}{}'.format(j, i)) for i in range(5)]

    fs = [FilePath(name='foo{}'.format(i)) for i in range(10)]
    f.hierarchy = Hierarchy(name='root',
                            children=fs + hs)
    f.configure_traits()
#============= EOF =============================================
