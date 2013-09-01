#===============================================================================
# Copyright 2013 Jake Ross
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
from traits.api import HasTraits, Str, List, Float, Int, Bool
from traitsui.api import View, Item
#============= standard library imports ========================
#============= local library imports  ==========================

# class UValue(HasTraits):
#     name = Str
#     value = Float
#     error = Float
#     citation = Str

class TableTaskEditor(HasTraits):
    title = Str('')
    table_num = Int(1)
    use_auto_title = Bool(False)
    subtitle_font_size = Int(8)
    def make_title(self):
        return '''<b>Table {}.</b><br/>
                  <font size={}>Ar/Ar data and constants used in age calculations.</font>
                  '''.format(self.table_num, self.subtitle_font_size)

#============= EOF =============================================
