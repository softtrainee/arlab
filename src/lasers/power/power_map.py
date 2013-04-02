#===============================================================================
# Copyright 2012 Jake Ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

#============= enthought library imports =======================
#============= standard library imports ========================
#============= local library imports  ==========================
from src.managers.data_managers.h5_data_manager import H5DataManager
from src.lasers.power.power_map_processor import PowerMapProcessor


def show():
    pmp = PowerMapProcessor()
    reader = H5DataManager()
    p = '/Users/ross/Sandbox/powermap.h5'
    reader.open_data(p)
#    if data.endswith('.h5') or data.endswith('.hdf5'):
#        reader = self._data_manager_factory()
#        reader.open_data(data)
#    else:
#        with open(data, 'r') as f:
#            reader = csv.reader(f)
#            #trim off header
#            reader.next()
#
    graph = pmp.load_graph(reader)
    graph.configure_traits()
#    self.graph.width = 625
#    self.graph.height = 500

#    reader.open_data(data)
#    z, _ = pmp._extract_h5(reader)
#    if self.surf:
#        self.graph3D.plot_data(z, func='surf',
#                               representation=self.representation,
#                               warp_scale=self.vertical_ex ,
#                               outline=self.surf_outline
#                               )
#    if self.contour:
#        self.graph3D.plot_data(z, func='contour_surf',
#                               contours=self.levels,
#                               warp_scale=self.vertical_ex,
#                               outline=self.contour_outline
#                               )



if __name__ == '__main__':
    show()
#============= EOF =============================================
