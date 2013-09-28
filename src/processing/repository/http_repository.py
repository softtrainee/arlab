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
from traits.api import HasTraits, Str

from src.loggable import Loggable
import urllib
import urllib2
#============= standard library imports ========================
#============= local library imports  ==========================
class HTTPRepository(Loggable):
    username = Str
    password = Str
    url = Str
    def post(self, path, body):
        if isinstance(body, dict):
            body = urllib.urlencode(body)

        host = self.url
        while host.endswith('/'):
            host = host[:-1]

        while path.startswith('/'):
            path = path[1:]

        url = '{}/{}'.format(host, path)
        try:
            with urllib2.urlopen(url, body) as f:
                resp = f.read()
                self._handle_post(resp)
        except urllib2.URLError:
            self.warning_dialog('Connection refused to {}'.format(url))

    def _handle_post(self, resp):
        print resp

    def _new_form(self, authenication=True):
        form = dict()
        if authenication:
            form['username'] = self.username
            form['password'] = self.password
        return form
#============= EOF =============================================
