'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#=============enthought library imports=======================
from traits.api import HasTraits, List
from traitsui.api import View, Item, Group

#=============standard library imports ========================

#=============local library imports  ==========================
class FusionsMotorConfigurer(HasTraits):
    '''
        G{classtree}
    '''
    motors = List
    def traits_view(self):
        '''
        '''

        motorgroup = Group(layout = 'tabbed')
        for m in self.motors:
            n = m.name
            self.add_trait(n, m)


            i = Item(n, style = 'custom', show_label = False)
            motorgroup.content.append(i)



        return View(motorgroup, resizable = True, title = 'Configure Motors',
                    buttons = ['OK', 'Cancel', 'Revert'],

                    )