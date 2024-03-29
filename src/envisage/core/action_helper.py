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

MANAGERS = []
def open_manager(app, man, **kw):
    ui = None
    if man in MANAGERS:
        try:
            man.ui.control.Raise()
        except AttributeError, e:
            print e
            ui = man.edit_traits(**kw)
    else:
        ui = man.edit_traits(**kw)

        MANAGERS.append(man)

    if app:
        if ui is not None and ui not in app.uis:
            app.uis.append(ui)

def open_protocol(app, protocol):
    m = app.get_service(protocol)

    open_manager(app, m)

def open_selector(db, app):
    db.application = app
    if db.connect():
        s = db._selector_factory()
        open_manager(app, s)
