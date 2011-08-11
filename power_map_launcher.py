#============= enthought library imports =======================

#============= standard library imports ========================
import os

#============= local library imports  ==========================
from src.data_processing.power_mapping.power_map_viewer import PowerMapViewer
from src.helpers import paths

if __name__ == '__main__':
    p = PowerMapViewer()

    root = os.path.join(paths.data_dir, 'powermap')
    p.set_data_files(root)
    p.configure_traits()
#============= EOF ====================================
