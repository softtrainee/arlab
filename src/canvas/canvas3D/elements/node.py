'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
import weakref
class Node(object):
    def __init__(self, *args):
        '''
      
        '''
        self.branches = []
        self.selectable = False
        self._accept = self.accept
        self.node_type = self.__class__.__name__
        self.parent = None
        self.name = None
        self.id = None
        self.add(*args)

    def render(self):
        '''

        '''
        pass

#    def clone(self):
#        '''
#        '''
#        return copy.copy(self)

    def __getitem__(self, i):
        '''
            @type i: C{str}
            @param i:
        '''
        return self.branches[i]

    def disable(self):
        '''
        '''
        if self.accept != self.disabled_accept:
            self._accept = self.accept
            self.accept = self.disabled_accept

    def enable(self):
        '''
        '''
        if self.accept != self._accept:
            self.accept = self._accept

    def disabled_accept(self, visitor):
        '''
            @type visitor: C{str}
            @param visitor:
        '''
        pass

    def accept(self, visitor):
        '''
            @type visitor: C{str}
            @param visitor:
        '''
        visitor.push_state(self)
        getattr(visitor, 'visit_' + self.node_type)(self)
        for node in self.branches:
            node.accept(visitor)
        visitor.pop_state(self)

    def add(self, *args):
        '''

        '''
        for arg in args:
            arg.parent = weakref.proxy(self)
            self.branches.append(arg)

    def remove(self, *args):
        '''
        '''
        for arg in args:
            self.branches.remove(arg)

    def update(self, **kw):
        '''
        '''
        self.__dict__.update(kw)
        return self


