#=============enthought library imports=======================
from traits.api import Any, Str

#=============standard library imports ========================
import ConfigParser
#=============local library imports  ==========================
from src.config_loadable import ConfigLoadable
class KerrDevice(ConfigLoadable):
    '''
        Base class for Kerr devices
    '''
    parent = Any
    address = Str('01')

    def ask(self, cmd, **kw):
        '''         
        '''
        return self.parent.ask(cmd, **kw)

    def tell(self, cmd, **kw):
        '''
        '''
        self.parent.tell(cmd, **kw)

    def load(self, path):
        '''
        '''

        config = ConfigParser.ConfigParser()
        config.read(path)

        self.set_attribute(config, 'address', 'General', 'address')
        self.load_additional_args(config)

#    def load_additional_args(self, config):
#        pass

    def _execute_hex_commands(self, commands):
        '''
        '''
        #commands list of tuples (addr,hex-command,delay,description)
        for cmd in commands:
            self._execute_hex_command(cmd)

    def _execute_hex_command(self, cmd, **kw):
        '''
        '''
        addr, cmd, delay, desc = cmd

        cmd = self._build_command(addr, cmd)
        r = None
        if cmd is not None:
            if desc:
                self.info(desc)

            r = self.ask(cmd, hex = True, delay = delay, **kw)

        return r

    def _build_command(self, addr, cmd):
        '''
        '''
        cmd = '{}{}'.format(addr, cmd)

        if self._check_command_len(cmd):
            chsum = self._calc_checksum(cmd)
            return 'AA{}{}'.format(cmd, chsum)

    def _check_command_len(self, cmd):
        '''
            the high nibble of the command sequence indicates the number of
            data bits to follow
        
        '''
        high_nibble = int(cmd[2:3], 16)
        data_bits = cmd[4:]

        return high_nibble == len(data_bits) / 2

    def _calc_checksum(self, cmd):
        '''
        '''
        sum = 0
        for i in range(0, len(cmd), 2):
            bit = cmd[i:i + 2]
            sum += int(bit, 16)

        r = '%02X' % sum
        return r[-2:]


    def _check_bits(self, bits):
        '''
        '''
        rbits = []
        for i in range(16):
            if (bits >> i) & 1 == 1:
                rbits.append(i)
        return rbits
#=========================EOF======================================