
def computeBCC(data_str):
    '''
        data str= ASCII string
        
        XOR each chr in string 
        
        returns a two char ASCII string
    '''
    bcc = 0
    for d in data_str:
        d = ord(d)
        bcc = bcc ^ d

    return '%02X' % bcc


def __generate_crc16_table():
    '''
    '''
    ''' Generates a crc16 lookup table

    .. note:: This will only be generated once
    '''
    result = []
    for byte in range(256):
        crc = 0x0000
        for _bit in range(8):
            if (byte ^ crc) & 0x0001:
                crc = (crc >> 1) ^ 0xa001
            else:
                crc >>= 1
            byte >>= 1
        result.append(crc)
    return result
__crc16_table = __generate_crc16_table()

def computeCRC(data, start_crc = 0xffff):
    '''
        @type start_crc: C{str}
        @param start_crc:
    '''
    ''' Computes a crc16 on the passed in data.
    @param data The data to create a crc16 of

    The difference between modbus's crc16 and a normal crc16
    is that modbus starts the crc value out at 0xffff.

    Accepts a string or a integer list
    '''
    crc = start_crc
    pre = lambda x: x
    if isinstance(data, str): pre = lambda x: ord(x)

    for a in data: crc = ((crc >> 8) & 0xff) ^ __crc16_table[
            (crc ^ pre(a)) & 0xff];

    #flip lo and hi bits
    crc = '%04x' % crc

    crc = '%s%s' % (crc[2:], crc[:2])
    return crc

def checkCRC(data, check):
    '''
        @type check: C{str}
        @param check:
    '''
    ''' Checks if the data matches the passed in CRC
    @param data The data to create a crc16 of
    @param check The CRC to validate
    '''
    return computeCRC(data) == check
#============= EOF ====================================
