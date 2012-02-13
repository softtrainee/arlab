'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
#=============enthought library imports=======================

#=============standard library imports ========================
import serial
import time
import glob
import os
import sys
import select

#=============local library imports  ==========================
from communicator import Communicator
from threading import currentThread


def get_ports():
    keyspan = glob.glob('/dev/tty.U*')
    usb = glob.glob('/dev/tty.usb*')
    return keyspan + usb


class SerialCommunicator(Communicator):
    '''
        Base Class for devices that communicate using a rs232 serial port.
        Using Keyspan serial converter is the best option for a Mac
        class is built on top of pyserial. Pyserial is used to create a handle and 
        this class uses the handle to read and write.
        handles are created when a serial device is opened
        setup args are loaded using load(). this method should be overwritten to
        load specific items.
    
    '''

    #char_write = False

    _auto_find_handle = False
    _auto_write_handle = False
    handle = None
    baudrate = None
    port = None
    bytesize = None
    parity = None
    stopbits = None
    timeout = None

    id_query = ''
    id_response = ''

    read_delay = 0
    def load(self, config, path):
        '''
           
        '''

        self.config_path = path
        self.config = config

        self.set_attribute(config, 'port', 'Communications', 'port')
        self.set_attribute(config, 'baudrate', 'Communications', 'baudrate',
                           cast='int', optional=True)
        self.set_attribute(config, 'bytesize', 'Communications', 'bytesize',
                           cast='int', optional=True)
        self.set_attribute(config, 'timeout', 'Communications', 'timeout',
                           cast='float', optional=True)

        parity = self.config_get(config, 'Communications', 'parity', optional=True)
        if parity is not None:
            self.parity = getattr(serial, 'PARITY_%s' % parity.upper())

        stopbits = self.config_get(config, 'Communications', 'stopbits', optional=True)
        if stopbits is not None:
            if stopbits == '1':
                stopbits = 'ONE'
            elif stopbits == '2':
                stopbits = 'TWO'
            self.stopbits = getattr(serial, 'STOPBITS_%s' % stopbits.upper())

        self.set_attribute(config, 'Communications', 'read_delay', 'read_delay', optional=True, default=0)

    def tell(self, cmd, is_hex=False, info=None, verbose=True, **kw):
        '''
           
        '''
        if self.handle is None:
            if verbose:
                info = 'no handle'
                self.log_tell(cmd, info)
            return
        
        with self._lock:
#            self._lock.acquire()
            self._write(cmd, is_hex=is_hex)
            if verbose:
                self.log_tell(cmd, info)

#        self._lock.release()

#    def write(self, *args, **kw):
#        '''
#        '''
#        self.info('%s' % args[0], decorate = False)
#
#        self._lock.acquire()
#        self._write(*args, **kw)
#        self._lock.release()

    def read(self, *args, **kw):
        '''
        '''
        with self._lock:
            #self._lock.acquire()
            r = self._read(*args, **kw)
            #self._lock.release()
            return r

    def ask(self, cmd, is_hex=False, verbose=True, delay=None, replace=None, remove_eol=True, info=None):
        '''
            
        '''

        if self.handle is None:
            if verbose:
                self.info('no handle    {}'.format(cmd))
            return

        #re=None
        with self._lock:
            self._write(cmd, is_hex=is_hex)
            re = self._read(is_hex=is_hex, delay=delay)

            re = self.process_response(re, replace, remove_eol)
    
            if verbose:
                #self.debug('lock acquired by {}'.format(currentThread().name))
                self.log_response(cmd, re, info)
                #self.debug('lock released by {}'.format(currentThread().name))
        return re

    def open(self, **kw):
        '''
            Use pyserial to create a handle connected to port wth baudrate 
            default handle parameters 
            baudrate=9600
            bytesize=EIGHTBITS
            parity= PARITY_NONE
            stopbits= STOPBITS_ONE
            timeout=None
        '''
        args = dict()

        ldict = locals()['kw']
        port = ldict['port'] if 'port' in ldict else None

        if port is None:
            port = self.port
            if port is None:
                self.warning('Port not set')
                return False

        #=======================================================================
        # #on windows device handles probably handled differently
        if sys.platform == 'darwin':
            port = '/dev/tty.{}'.format(port)
        #=======================================================================

        args['port'] = port

        for key in ['baudrate', 'bytesize', 'parity', 'stopbits', 'timeout']:
            v = ldict[key] if key in ldict else None
            if v is None:
                v = getattr(self, key)
            if v is not None:
                args[key] = v

        pref = kw['prefs'] if 'prefs' in kw else None
        if pref is not None:
            pref = pref.serial_preference
            self._auto_find_handle = pref.auto_find_handle
            self._auto_write_handle = pref.auto_write_handle

        self.simulation = True
        if self._validate_address(port):
            try_connect = True
            while try_connect:
                try:
                    self.handle = serial.Serial(**args)
                    try_connect = False
                    self.simulation = False

                except serial.serialutil.SerialException:
                    try_connect = False
        elif self._auto_find_handle:
            self._find_handle(args, **kw)

        connected = True if self.handle is not None else False

        return connected

    def _find_handle(self, args, **kw):
        found = False
        self.simulation = False
        self.info('Trying to find correct port')

        port = None
        for port in get_ports():
            self.info('trying port {}'.format(port))
            args['port'] = port
            try:
                self.handle = serial.Serial(**args)
            except serial.SerialException:
                continue

            r = self.ask(self.id_query)

            #use id_response as a callable to do device specific 
            #checking
            if callable(self.id_response):
                if self.id_response(r):
                    found = True
                    self.simulation = False
                    break

            if r == self.id_response:
                found = True
                self.simulation = False
                break

        if not found:

            #update the port
            if self._auto_write_handle and port:
                #port in form
                #/dev/tty.USAXXX1.1
                p = os.path.split(port)[-1]
                #remove tty.
                p = p[4:]

                self.config.set('Communication', 'port',)
                self.write_configuration(self.config, self.config_path)

            self.handle = None
            self.simulation = True

    def _validate_address(self, port):
        '''
            use glob to check the avaibable serial ports 
            valid ports start with /dev/tty.U or /dev/tty.usbmodem
    
        '''
        valid = get_ports()
        if port in valid:
            return True
        else:
            self.warning('{} is not a valid port address'.format(port))
            if not valid:
                self.warning('No valid ports')
            else:
                for v in valid:
                    self.warning(v)

#            valid = '\n'.join(['%s' % v for v in valid])
#            self.warning('''%s is not a valid port address
#==== valid port addresses ==== \n%s''' % (port, valid))

    def _write(self, cmd, is_hex=False):
        '''
            use the serial handle to write the cmd to the serial buffer 
            
        '''
        def write(cmd_str):
            try:
                self.handle.write(cmd_str)
            except (serial.serialutil.SerialException, OSError, IOError), e:
                self.warning(e)

        if not self.simulation:

            if is_hex:
                cmd = cmd.decode('hex')
                #write(cmd)
            else:
                if self._terminator is not None:
                    cmd += self._terminator

#                if self.char_write:
#                    for c in cmd:
#                        write(c)
#                        time.sleep(0.0005)
#                else:
#                    write(cmd)
            #print cmd, len(cmd)
#            time.sleep(50e-9)
            write(cmd)

    def _read(self, is_hex=False, time_out=1, delay=None):
        '''
            use the serial handle to read available bytes from the serial buffer
            
        '''
        def eread(inw):
            r = None
            try:
                r = self.handle.read(inw)
            except (OSError, IOError), e:
                self.warning(e)
            return r

        def get_chars():
            c = 0
            try:
                c = self.handle.inWaiting()
            except (OSError, IOError), e:
                self.warning(e)
            return c

        def get_line():
            inw = get_chars()
            r = eread(inw)
            isline = r.endswith('\n') or r.endswith('\r') if r else False
            return isline, r, inw

        r = None
        if self.simulation:
            r = 'simulation'
        else:
            inw = 0
            if delay is not None:
                time.sleep(delay / 1000.)
                inw = get_chars()
                r = eread(inw)
            else:
                time.sleep(self.read_delay)
                ready_to_read, _, _ = select.select([self.handle], [], [], 0.5)
                if ready_to_read:
                    isline, r, c = get_line()
                    if not isline:
                        pcnt = 0
                        cnt = 0
                        for _ in xrange(8000):
                            isline, r, c = get_line()
                            if isline:
                                break

                            if pcnt == c:
                                cnt += 1
                            else:
                                cnt = 0

                            pcnt = c
                            if cnt > 500:
                                break

            if is_hex:
                r = ''.join(['{:02X}'.format(ri) for ri in map(ord, r)])

        return r
#            if inw > 0:
#                try:
#                    r = self.handle.read(inw)
##                    self.handle.flush()
#                    if is_hex:
#                        r = ''.join(['{:02X}'.format(ri) for ri in map(ord, r)])
##                        rr = ''
##                        for ri in r:
##                            rr += '{:02X}' % ord(ri)
##                        r = rr
#
#                except (OSError, IOError), e:
#                    self.warning(e)

#        else:
#            r = 'simulation'
#
#        return r
#===================== EOF ==========================================
