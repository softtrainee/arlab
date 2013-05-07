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
from traits.api import HasTraits, Instance, Any, Str
from traitsui.api import View, Item, TableEditor
from src.displays.html_display import HTMLDisplay
from src.database.adapters.isotope_adapter import IsotopeAdapter
from src.database.records.isotope_record import IsotopeRecord
from src.database.isotope_analysis.analysis_display import AnalysisDisplay

#============= standard library imports ========================
#============= local library imports  ==========================



class Demo(HasTraits):
    display = Instance(HTMLDisplay)
    view = View(Item('display', show_label=False, style='custom'),
                resizable=True,
                width=600,
                height=500
                )

    def _display_default(self):
        db = IsotopeAdapter(host='localhost',
                            name='isotopedb_dev',
                            kind='mysql',
                            username='root', password='Argon')
        if db.connect():
            lns = db.get_labnumber(6)
            r = IsotopeRecord(_dbrecord=lns.analyses[-1])
            r.load_graph()

            return AnalysisDisplay(record=r)

if __name__ == '__main__':
    d = Demo()
    d.configure_traits()
#============= EOF =============================================
