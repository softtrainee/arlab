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
#=============standard library imports =======================
import struct
import binascii
#=============local library imports  =========================
from serial_communicator import SerialCommunicator
from src.hardware.core.checksum_helper import computeCRC
class ModbusCommunicator(SerialCommunicator):
    '''
        modbus message syntax
        [Device address][function code][data][error check]
    
    '''

    slave_address = '01'
    device_word_order = 'low_high'

    _write_func_code = '06'

    scheduler = None

    def load(self, config, path):
        '''
            
        '''
        #super(ModbusCommunicator, self).load(config, path)
        SerialCommunicator.load(self, config, path)
        self.set_attribute(config, 'slave_address', 'Communications', 'slave_address')

    def write(self, register, value, nregisters=1, response_type='register_write', **kw):
        '''
        '''
        if nregisters == 1:
            return self.set_single_register(register, value, response_type, **kw)
        else:
            return self.set_multiple_registers(register, nregisters, value, response_type, **kw)

    def tell(self, *args, **kw):
        return self.write(*args, **kw)

    def read(self, register, response_type='float', nregisters=1, **kw):
        '''            
        '''
        return self.read_holding_register(register, nregisters, response_type, **kw)

    def _execute_request(self, args, response_type, **kw):
        '''
        '''
        cmd = ''.join([self.slave_address] + args)

        #convert hex string into list of ints
        cmdargs = self._parse_hexstr(cmd, return_type='int')

        #calculate the CRC and append to message
        crc = computeCRC(cmdargs)
        cmd += crc

        kw['hex'] = True

        if self.scheduler is not None:
            resp = self.scheduler.schedule(self.ask, args=(cmd,),
                                           kwargs=kw
                                           )
        else:
            resp = self.ask(cmd, **kw)

        return self._parse_response(resp, response_type)

    def _parse_hexstr(self, hexstr, return_type='hex'):
        '''
        '''
        gen = range(0, len(hexstr), 2)
        if return_type == 'int':
            return [int(hexstr[i:i + 2], 16) for i in  gen]
        else:
            return [hexstr[i:i + 2] for i in gen]

    def _parse_response(self, resp, response_type):
        '''
        '''
        if resp is not None and resp is not 'simulation':

            args = self._parse_hexstr(resp)

            #check the crc
            cargs = self._parse_hexstr(resp, return_type='int')

            crc = ''.join(args[-2:])
            calc_crc = computeCRC(cargs[:-2])
            if not crc.upper() == calc_crc.upper():
                self.warning('Returned CRC ({}) does not match calculated ({})'.format(crc, calc_crc))
                self.handle.flushInput()
            else:
                if response_type == 'register_write':
                    return True
                ndata = int(args[2], 16)
                data = ''.join(args[3:3 + ndata])
                dataargs = args[3:3 + ndata]
                if len(dataargs) < ndata:
                    ndata = 4
                    dataargs = args[3:3 + ndata]

                if ndata > 2:
                    low_word = ''.join(dataargs[:2])
                    high_word = ''.join(dataargs[2:])

                    if self.device_word_order == 'low_high':
                        '''
                        dataargs in low word - high word order
                        1234 5678
                        want high word -low word order
                        5678 1234
                        '''

                        data = ''.join([high_word, low_word])
                    else:
                        data = ''.join([low_word, high_word])
                else:
                    data = '0000'.join(dataargs)

                return struct.unpack('!f', data.decode('hex'))[0] if response_type == 'float' \
                        else int(data, 16)


    def set_multiple_registers(self, startid, nregisters, value, response_type, **kw):
        '''
        '''

        func_code = '10'
        data_address = '{:04X}'.format(int(startid))
        n = '{:04X}'.format(int(nregisters))
        nbytes = '{:02X}'.format(int(nregisters * 2))

        #convert decimal value to 32-bit float
        binstr = struct.pack('!f', value)

        #convert binary string to a ascii hex string
        hexstr = binascii.hexlify(binstr)
        if self.device_word_order == 'low_high':
            high = hexstr[:4]
            low = hexstr[4:]

            #flip order of words
            value = ''.join([low, high])
        else:
            value = hexstr

        return self._execute_request([func_code, data_address, n, nbytes, value], response_type, **kw)

    def set_single_register(self, rid, value, response_type, **kw):
        '''
        '''


        #func_code = '06'
        func_code = self._write_func_code
        register_addr = '{:04X}'.format(int(rid))
        value = '{:04X}'.format(int(value))
        return self._execute_request([func_code, register_addr, value], response_type, **kw)

    def read_holding_register(self, holdid, nregisters, response_type, **kw):
        '''         
        '''
        func_code = '03'
        data_address = '{:04X}'.format(holdid)
        n = '{:04X}'.format(nregisters)
        return self._execute_request([func_code, data_address, n], response_type, **kw)

    def read_input_status(self, inputid, ninputs):
        '''
        '''
        func_code = '02'
        data_address = '{:04X}'.format(inputid - 10001)
        n = '{04x}'.format(ninputs)
        return self._execute_request([func_code, data_address, n])


