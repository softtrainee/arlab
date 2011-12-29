'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#============= enthought library imports =======================
from data_manager import DataManager

#============= standard library imports ========================
import csv
#============= local library imports  ==========================
class CSVDataManager(DataManager):
    '''
    '''

    def write_metadata(self, md, frame_key=None):

        sline = ['#<metadata>===================================================']
        eline = ['#</metadata>===================================================']
        data = [sline] + md + [eline]
        self.write_to_frame(data, frame_key)

    def write_to_frame(self, datum, frame_key=None):

        if frame_key is None:
            frame_key = self._current_frame

        frame = self._get_frame(frame_key)
        if frame is not None:
            self.new_writer(frame, datum)

    def new_writer(self, p, datum, append=True):
        '''

        '''
        mode = 'w'
        if append:
            mode = 'a'
        with open(p, mode) as f:
            writer = csv.writer(f)
            if isinstance(datum[0], (list, tuple)):
                writer.writerows(datum)
            else:
                writer.writerow(datum)



#============= EOF ====================================
