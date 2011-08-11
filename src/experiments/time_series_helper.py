#============= enthought library imports =======================

#============= standard library imports ========================
import struct
#============= local library imports  ==========================
def build_time_series_blob(ts, vs):
    '''
        @type vs: C{str}
        @param vs:
    '''
    if isinstance(ts, float):
        ts = [ts]
        vs = [vs]
    blob = ''
    for ti, vi in zip(ts, vs):
        blob += struct.pack('>ff', float(vi), float(ti))
    return blob

def parse_time_series_blob(blob):
    '''
    '''
    v = []
    t = []
    for i in range(0, len(blob), 8):
        vi, ti = struct.unpack('>ff', blob[i:i + 8])
        v.append(vi)
        t.append(ti)

    return t, v
#============= EOF ====================================
