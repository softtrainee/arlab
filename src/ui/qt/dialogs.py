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
# from traits.api import HasTraits
from pyface.confirmation_dialog import ConfirmationDialog
from pyface.api import OK
import time
from threading import Event
from src.ui.gui import invoke_in_main_thread
from pyface.message_dialog import MessageDialog

#============= enthought library imports =======================
#============= standard library imports ========================
#============= local library imports  ==========================
class myMessageMixin(object):
    '''
        makes  message dialogs thread save. 
    
    '''
    timeout_return_code=OK
    
    def open(self, timeout=None):
        '''        
            open the confirmation dialog on the GUI thread but wait for return 
        '''
        evt = Event()
        invoke_in_main_thread(self._open, evt)
        st=time.time()
        while not evt.is_set():
            time.sleep(0.05)
            if time.time()-st>timeout:
                self.close()
                return self.timeout_return_code
            
        return self.return_code

    def _open(self, evt):

        if self.control is None:
            self._create()

        if self.style == 'modal':
            self.return_code = self._show_modal()
            self.close()

        else:
            self.show(True)
            self.return_code = OK

        evt.set()
        return self.return_code

class myMessageDialog(myMessageMixin, MessageDialog):
    pass
class myConfirmationDialog(myMessageMixin, ConfirmationDialog):
    pass









#============= EOF =============================================
