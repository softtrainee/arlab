#============= enthought library imports =======================
from traits.api import HasTraits

#============= standard library imports ========================

#============= local library imports  ==========================
class DatabaseItem(HasTraits):
    def get_items(self, id):
        '''
            @type id: C{str}
            @param id:
        '''
        print getattr(self, '_%s' % id)
        return [i[1] for i in getattr(self, '_%s' % id)]

    def get_id(self, id):
        '''
            @type id: C{str}
            @param id:
        '''
        attr = getattr(self, id)
        for i in getattr(self, '_%s' % id):
            if i[1] == attr:
                return int(i[0])
#============= views ===================================
#============= EOF ====================================
