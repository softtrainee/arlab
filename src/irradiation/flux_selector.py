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
from traits.api import HasTraits, Any, Str, Property, cached_property
from traitsui.api import View, Item, EnumEditor, HGroup, spring
#============= standard library imports ========================
#============= local library imports  ==========================


class FluxSelector(HasTraits):
    db = Any
    flux_monitor = Str
    flux_monitors = Property


    def traits_view(self):
        v = View(HGroup(Item('flux_monitor', show_label=False,
                             editor=EnumEditor(name='flux_monitors')),
                        spring
                        )
                 )
        return v

#===============================================================================
# handlers
#===============================================================================
    def _edit_monitor_button_fired(self):

        names = self.flux_monitors
        monitor = FluxMonitor(names=names)
        info = monitor.edit_traits(kind='livemodal')
        if info.result:
            db = self.db
            kw = dict(age=monitor.age,
                       age_err=monitor.age_err,
                       decay_constant=monitor.decay_constant,
                       decay_constant_err=monitor.decay_constant_err)

            dbmonitor = db.get_flux_monitor(monitor.name)
            if dbmonitor:
                for k, v in kw.iteritems():
                    setattr(dbmonitor, k, v)
            else:
                db.add_flux_monitor(monitor.name, **kw)
                self.flux_monitor = monitor.name

            db.commit()
            self.saved = True
#===============================================================================
# property get/set
#===============================================================================
    @cached_property
    def _get_flux_monitors(self):
        db = self.db
        fs = db.get_flux_monitors()
        if fs:
            fs = [fi.name for fi in db.get_flux_monitors()]
        else:
            fs = []
        return fs
#============= EOF =============================================
