#@PydevCodeAnalysisIgnore

#============= enthought library imports =======================

#============= standard library imports ========================

#============= local library imports  ==========================
from src.scripts.file_script import FileScript

class LaserScript(FileScript):
    def clean_up(self):
        '''
        '''
        fr = self.manager.failure_reason
        if self.user_cancel:
            self.info('run canceled by user')
        elif fr is not None:
            self.info('%s' % fr)

        self.manager.disable_laser()
#============= EOF ====================================
