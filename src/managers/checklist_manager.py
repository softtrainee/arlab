#'''
#@author: Jake Ross
#@copyright: 2009
#@license: Educational Community License 1.0
#'''
##=============enthought library imports=======================
#from traits.api import HasTraits, Instance, Bool, Str, Float, Button, Any, List, Enum
#from traitsui.api import View, Item, HGroup, VGroup, \
#    TabularEditor, TreeNode, TreeEditor
#from traitsui.tabular_adapter import TabularAdapter
##=============standard library imports ========================
##import time
##from subprocess import call
#import os
##=============local library imports  ==========================
#from filetools import parse_setupfile
#from runs.check_list_run import ChecklistRun
#from manager import Manager
#
#class CheckItem(HasTraits):
#    '''
#        G{classtree}
#    '''
#    command = Str
#    interval = Float
#
#class CLAdapter(TabularAdapter):
#    '''
#        G{classtree}
#    '''
#    columns = [('Command', 'command'),
#             ('Interval', 'interval')]
#    def get_bg_color(self, obj, trait, row):
#        '''
#            @type obj: C{str}
#            @param obj:
#
#            @type trait: C{str}
#            @param trait:
#
#            @type row: C{str}
#            @param row:
#        '''
#        if row % 2 == 0:
#            return (0, 100, 255, 50)
#        else:
#            return (255, 255, 255)
#class Checklist(Manager):
#    '''
#        G{classtree}
#    '''
#    name = Str
#
#    _dclicked = Any
#
#    commands = List(CheckItem)
#    display_checklist = List(CheckItem)
#    start = Button('start')
#    pause = Button('pause')
#    _started = Bool(False)
#    _paused = Bool(False)
#    voice = Enum('bruce', 'fred', 'junior', 'ralph', 'alex',
#               'agnes', 'vicki', 'victoria', 'princess', 'kathy')
#    def __init__(self, root, *args, **kw):
#        '''
#            @type root: C{str}
#            @param root:
#
#        '''
#        super(Checklist, self).__init__(*args, **kw)
#        self.load_checklist(os.path.join(root, self.name))
#    def load_checklist(self, p):
#        '''
#            @type p: C{str}
#            @param p:
#        '''
#        ch = self.commands
#        rows = parse_setupfile(p)
#        for r in rows:
#            rr = r[0].split(':')
#
#            if len(rr) == 2:
#                interval = rr[1]
#            else:
#                interval = 2
#            ch.append(CheckItem(command = rr[0], interval = float(interval)))
#    def _start_fired(self):
#        '''
#        '''
#        self._started = True
#        if not self._paused:
#            self.display_checklist = []
#            self.runner = ChecklistRun(self)
#        self.runner.start()
#    def _pause_fired(self):
#        '''
#        '''
#        self._paused = True
#        ind = self.runner.get_index()
#
#        self.runner.stop()
#
#        self.runner = ChecklistRun(self)
#        self.runner.commands = self.commands[ind + 1:]
#    def __dclicked_changed(self):
#        '''
#        '''
#        index = self._dclicked.row
#        if self.runner.isAlive():
#            self.runner.stop()
#
#        ch = self.commands[index:]
#        self.display_checklist = self.display_checklist[:index]
#
#        self.runner = ChecklistRun(self)
#        self.runner.commands = ch
#        self.runner.start()
#class CGroup(HasTraits):
#    '''
#        G{classtree}
#    '''
#    name = Str
#    checklists = List(Checklist)
#class ChecklistDirectory(HasTraits):
#    '''
#        G{classtree}
#    '''
#    name = 'Check Lists'
#    cgroups = List(CGroup)
#class ChecklistManager(HasTraits):
#    '''
#        G{classtree}
#    '''
#    cldir = Instance(ChecklistDirectory)
#
#    def load_checklists(self, root):
#        '''
#            @type root: C{str}
#            @param root:
#        '''
#        self.cldir = cld = ChecklistDirectory()
#
#        dirs = os.listdir(root)
#        for d in dirs:
#
#            r = os.path.join(root, d)
#            if os.path.isdir(r):
#                ch = os.listdir(r)
#                cl = [Checklist(r, name = ci) for ci in ch if ci[0] != '.']
#                cld.cgroups.append(CGroup(name = d, checklists = cl))
#
#    def traits_view(self):
#        '''
#        '''
#        buttongrp = HGroup(Item('start', enabled_when = 'not _started'),
#                         Item('pause', enabled_when = '_started'),
#                         Item('voice'), show_labels = False)
#
#        nodes = [
#                TreeNode(node_for = [ChecklistDirectory],
#                         auto_open = True,
#                         label = 'name',
#                         view = View(),
#                         children = 'cgroups'),
#                TreeNode(node_for = [CGroup],
#                         auto_open = True,
#                         label = 'name',
#                         view = View(),
#                         children = 'checklists'),
#                TreeNode(node_for = [Checklist],
#                         auto_open = True,
#                         label = 'name',
#                         view = View(VGroup(
#                             Item('display_checklist', editor = TabularEditor(adapter = CLAdapter(),
#                                                     selected = '_selected',
#                                                     dclicked = '_dclicked'
#                                                     ), show_label = False, width = 0.65),
#                             buttongrp,
#
#                             )))
#                ]
#        tree_editor = TreeEditor(nodes = nodes)
#
#        v = View(Item('cldir', editor = tree_editor, show_label = False),
#                width = 500,
#                height = 300,
#                resizable = True
#                )
#        return v
##============= EOF ====================================
