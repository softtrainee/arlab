#============= enthought library imports =======================
from pyface.action.api import Action

#============= standard library imports ========================

#============= local library imports  ==========================

class UpdateToHeadAction(Action):
    '''
        G{classtree}
    '''
    description = 'Update Pychron to the head revision'
    name = 'Update to head'
    def perform(self, event):
        '''
            @type event: C{str}
            @param event:
        '''
        app = event.window.application
        client = app.get_service('src.svn.svn_client.SVNClient')
        client.update_to_head()

#============= EOF ====================================
