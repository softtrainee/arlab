#============= enthought library imports =======================
from traits.api import Dict

#============= standard library imports ========================
import os

#============= local library imports  ==========================
from src.helpers import paths
from src.helpers.filetools import unique_path
from src.managers.manager import Manager

class DataManager(Manager):
    '''
    '''
    _extension = 'txt'
    frames = Dict
    _current_frame = ''

    def new_frame(self, *args, **kw):
        '''
        '''
        p = self._new_frame_path(*args, **kw)

        name, _ext = os.path.splitext(os.path.basename(p))
        self.frames[name] = p

        self._current_frame = name
        return name

    def _new_frame_path(self, path = None, directory = 'streams', base_frame_name = None):
        '''

        '''
        if base_frame_name is None:
            base_frame_name = 'run'

        base = os.path.join(paths.data_dir, directory)
        if not os.path.isdir(base):
            os.mkdir(base)

        if path is None:
            path = unique_path(base, base_frame_name, filetype = self._extension)

        self.info('New frame {}'.format(path))
        return path



#============= EOF ====================================
