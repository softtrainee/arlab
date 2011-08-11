#@PydevCodeAnalysisIgnore

#============= enthought library imports =======================
#from traits.api import HasTraits, on_trait_change,Str,Int,Float,Button
#from traitsui.api import View,Item,Group,HGroup,VGroup

#============= standard library imports ========================
import time
import os
#============= local library imports  ==========================
from src.helpers.paths import data_dir
from laser_script import LaserScript
from src.helpers.filetools import unique_path

class BeamScanScript(LaserScript):
    '''
        G{classtree}
    '''
    video_record = False
    def load_file(self):
        '''
        '''
        self.video_record = self._file_contents_.pop(0) in ['true', 'TRUE', 'T', 't']
        self.request_power = float(self._file_contents_.pop(0))

    def _run_(self):
        '''
        '''
        manager = self.manager
        vm = manager.video_manager
        if self.video_record:
            p = unique_path(os.path.join(data_dir, 'beamscans'),
                          'video',
                          filetype = 'avi'
                          )
            vm.start()
            vm.start_recording(p)


        manager.enable_laser()
        manager.set_laser_power(self.request_power)


        delay = 5
        for line in self._file_contents_:
            if not self.isAlive():
                break
            bd = float(line)
            self.add_display_text('Beam diameter %0.1f' % bd)
            manager.set_beam_diameter(bd)

            msg = 'waiting at %0.1f for %i sec' % (bd, delay)
            self.add_display_text(msg, log = True)

            time.sleep(delay)

        self.clean_up()
        if self.video_record:
            vm.stop_recording()
        self.add_display_text('beam scan complete', log = True)

#============= EOF ====================================
