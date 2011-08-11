'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#=============enthought library imports=======================
from traits.api import HasTraits
from pyface.timer.api import Timer
#=============standard library imports ========================
from threading import Lock#, Thread
#=============local library imports  ==========================


class Streamable(HasTraits):
    '''
        G{classtree}
    '''
    stream_manager = None
#    current_value = 0.0
    #block = False
    scan_func = None
    stream_lock = None
    timer = None
    scan_period = 1000

    def target(self, *args, **kw):
        '''
        '''
        self.stream_lock.acquire()

        self._scan_(*args, **kw)
        self.stream_lock.release()

    def _scan_(self, *args):
        '''

        '''
        if self.scan_func:
            try:
                v = getattr(self, self.scan_func)()
            except AttributeError:
                return

            if v is not None:
#                if isinstance(v, tuple):
#                    self.current_value = v[0]

                if self.stream_manager is not None:
                    self.stream_manager.record(v, self.name)

    def scan(self, *args, **kw):
        '''

        '''
        if self.stream_lock is None:
            self.stream_lock = Lock()

        #if self.block:
            #self.current_value = 0
            #return 0
        #else:
        self.target()
        #Thread(target = self.target, args = args, kwargs = kw).start()

    def start_scan(self):
        if self.timer is not None:
            self.timer.Stop()

        if self.connected:
            self.info('Starting scan')
            self.timer = Timer(self.scan_period, self.scan)
            self.timer.Start()

    def stop_scan(self):
        if self.timer is not None:
            self.timer.Stop()