#===============================================================================
# Copyright 2011 Jake Ross
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
from traits.api import HasTraits, String
from traitsui.api import View, Item, HTMLEditor


#============= standard library imports ========================

#============= local library imports  ==========================

#============= views ===================================
class HelpView(HasTraits):
    help_message = String('<body bgcolor = "#ffffcc" text = "#000000"></body>')

    def selected_update(self, obj, name, old, new):
        if hasattr(new, '_script'):
            doc = new._script.get_documentation()

            if doc is not None:
                self.help_message = str(doc)


    def traits_view(self):
        v = View(Item('help_message',
                    editor=HTMLEditor(),
                     show_label=False))
        return v
