def make_bitarray(data, width = 8):
    '''
        @type width: C{str}
        @param width:
    '''
    ba = ''.join(str((data >> i) & 1) for i in xrange(width - 1, -1, -1))

    return ba


