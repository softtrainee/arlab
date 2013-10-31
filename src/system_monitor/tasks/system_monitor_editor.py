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
from threading import Thread
import time
from traits.api import Instance, Property, Int, Bool

#============= standard library imports ========================
#============= local library imports  ==========================
from src.messaging.notify.subscriber import Subscriber
from src.processing.plotter_options_manager import SystemMonitorOptionsManager
from src.processing.tasks.figures.editors.series_editor import SeriesEditor
from src.system_monitor.tasks.connection_spec import ConnectionSpec
from src.system_monitor.tasks.controls import SystemMonitorControls
from src.ui.gui import invoke_in_main_thread

"""
    subscribe to pyexperiment
    or poll database for changes

"""


class SystemMonitorEditor(SeriesEditor):
    conn_spec = Instance(ConnectionSpec, ())
    name = Property(depends_on='conn_spec:+')
    tool = Instance(SystemMonitorControls)
    subscriber = Instance(Subscriber)
    plotter_options_manager_klass = SystemMonitorOptionsManager

    _sub_str = 'RunAdded'

    use_poll = Bool(False)
    _poll_interval = Int
    _polling = False

    def prepare_destroy(self):
        self._polling = False
        self.subscriber.stop()

    def _subscriber_default(self):
        h = self.conn_spec.host
        p = self.conn_spec.port
        s = self._sub_str

        self.info('starting subscription to {}:{} "{}"'.format(h, p, s))
        sub = Subscriber(host=self.conn_spec.host,
                         port=self.conn_spec.port)
        return sub

    def start(self):
        sub = self.subscriber
        sub.connect()
        sub.subscribe(self._sub_str)
        sub.listen(self.sub_refresh_plots)

        if self.use_poll:
            t = Thread(name='poll', target=self._poll)
            t.setDaemon(True)
            t.start()

    def _poll(self):
        self._polling = True
        last_run_uuid = self._get_last_run_uuid()
        while self._polling:
            time.sleep(self._poll_interval)

            lr = self._get_last_run_uuid()
            if lr != last_run_uuid:
                last_run_uuid = lr
                invoke_in_main_thread(self.sub_refresh_plots, lr)

    def _get_last_run_uuid(self):
        db = self.processor.db
        with db.session_ctx():
            dbrun = db.get_last_analysis(spectrometer=self.conn_spec.system_name)
            if dbrun:
                return dbrun.uuid

    def sub_refresh_plots(self, last_run_uuid=None):
        """
            get the last n runs for this system
        """
        proc = self.processor
        db = proc.db

        with db.session_ctx():
            dbrun = db.get_analysis_uuid(last_run_uuid)
            if not dbrun:
                dbrun = db.get_last_analysis(spectrometer=self.conn_spec.system_name)

            if dbrun:
                an = proc.make_analysis(dbrun)
                analysis_type = an.analysis_type
                ms = an.mass_spectrometer
                ed = an.extract_device

                weeks = 0
                days = 0
                hours = 12

                proc.analysis_series(analysis_type, ms, ed, weeks, days, hours)

    def _tool_default(self):
        tool = SystemMonitorControls()

        keys = ('Ar40',)
        fits = ('',)
        tool.load_fits(keys, fits)
        return tool

    def _set_name(self):
        pass

    def _get_name(self):
        return '{}-{}'.format(self.conn_spec.system_name,
                              self.conn_spec.host)

        #============= EOF =============================================
