#===============================================================================
# Copyright 2011 Jake Ross
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
import psutil
import os
import gc
import sys
import cPickle
from src.helpers.filetools import unique_path
from itertools import groupby
import objgraph
import random
import inspect
import subprocess
USE_MEM_LOG = True
root = os.path.join(os.path.expanduser('~'), 'Desktop', 'memtest')
if not os.path.isdir(root):
    os.mkdir(root)

p, _ = unique_path(root, 'mem')
def write_mem(msg, m):
    with open(os.path.join(root, p), 'a') as fp:
        fp.write('{:<50s}:{}\n'.format(msg, m))


PID = None
def mem_break():
    write_mem('#' + '=' * 49, '')

def mem_log(msg):
    if USE_MEM_LOG:
        mem = _get_current_mem()
        write_mem(msg, mem)

def mem_log_func(func, *args, **kw):
    n = func.func_name
    mem_log('pre {}'.format(n))
    r = func(*args, **kw)
    mem_log('post {}'.format(n))
    return r

def mem_available():
    mem = psutil.avail_phymem()
    return mem * 1024.** -2
#     mem=_get_current_mem()


def mem_dump(path):
    dump = open(os.path.join(root, path), 'w')
    with dump as fp:
        for obj in gc.get_objects():
            i = id(obj)
            size = sys.getsizeof(obj, 0)
            if size > 1000:
                #    referrers = [id(o) for o in gc.get_referrers(obj) if hasattr(o, '__class__')]
                referents = [id(o) for o in gc.get_referents(obj) if hasattr(o, '__class__')]
                if hasattr(obj, '__class__'):
                    cls = str(obj.__class__)

                    if hasattr(obj, 'name'):
                        name = obj.name
                    else:
                        name = obj.__class__.__name__

                    fp.write('id: {:<10s} name: {:<10s} class: {:<50s} size: {:<10s} referents:{}\n'.format(str(i), name,
                                                                                                            cls,
                                                                                                            str(size),
                                                                                                            len(referents),
                                                                                                            )
                             )
                    if isinstance(obj, dict):
                        keys = ','.join(map(str, obj.keys()))
                        fp.write('keys: {}'.format(keys))

#                 cPickle.dump({'id': i, 'class': cls, 'size': size, 'referents': referents, 'name':name}, dump)


def mem_sort():
    dump = open(os.path.join(root, 'gcmem.pickle'), 'r')
    objs = []
    i = 0
    while dump:
        try:
            obj = cPickle.load(dump)
            objs.append(obj)
        except EOFError:
            pass
#         if i>10000:
#             break

        i += 1
    with open(os.path.join(root, 'gcmem.pickle.sorted'), 'w') as fp:
        for oi in sorted(objs, key=lambda x: x['size'], reverse=True):
            fp.write('{name} {size} {referents}\n'.format(**oi))

#     with open(os.path.join(root, 'gcmem.txt'), 'w') as fp:

def _get_current_mem():
    PID = os.getpid()
    proc = psutil.Process(PID)
    mem = proc.get_memory_info()
    return mem.rss / 1024.**2


class MemCTX(object):
    def __init__(self, cls):
        self._cls = cls
    def __enter__(self):
        print 'enter'
#         self._before = [id(o) for o in gc.get_objects() if isinstance(o, self._cls)]
        self._before = [id(o) for o in gc.get_objects() if self._cls in str(type(o))]
        print len(self._before)

    def __exit__(self, *args, **kw):
        print 'exit'
        gc.collect()
        bf = self._before
        cls = self._cls
        objs = [o for o in gc.get_objects()
                    if self._cls in str(type(o))
#                     if isinstance(o, cls)
                    ]

        print len(objs), len(bf)
        objs = [o for o in objs if not id(o) in bf]
        print 'new objs {}'.format(len(objs))
        if len(objs) < 100:
            for oi in objs:
                print oi, [type(oo) for oo in gc.get_referrers(oi)]

        return
        path = os.environ['PATH']
        os.environ['PATH'] = '{}:/usr/local/bin'.format(path)
        fn = '/Users/ross/Desktop/chain.png'
        objgraph.show_chain(
                    objgraph.find_backref_chain(

                                                random.choice(objs),
                                                inspect.ismodule),
                    filename=fn)
#
        subprocess.call(['open', fn])



from collections import defaultdict


def measure_type(cls=None, group=None):
    d = defaultdict(int)
    if cls:
        d[cls] = sum((1 for o in gc.get_objects() if type(o) == cls))
    else:
        objs = gc.get_objects()
        if group:
            objs = filter(lambda x: group in str(type(x)), objs)

        for i in objs:
            d[type(i)] += 1

    return d

# gp, _ = unique_path(root, 'growth')
def calc_growth(before, cls=None, group=None, count=None, write=False):
    gc.collect()

    after = measure_type(cls, group)
#     after = end_growth()
    ts = 0
    for k, v in sorted([(ki, after[ki] - before[ki]) for ki in after if after[ki] - before[ki] > 1],
                      key=lambda x:x[1],
                      reverse=True
                      ):
#         if cls and v > 1 :
#             obj = get_type(k).next()
#             print 'referrers'
#             for ri in gc.get_referrers(obj):
#                 print ri
#
#             print 'referrents'
#             for ri in gc.get_referents(obj):
#                 print ri

        s = get_size(k)
        if group:
            ts += s
        msg = '{:<70s}: {} size: {}'.format(k, v, s)
        print msg
#         if write:
#             with open(gp, 'a') as fp:
#                 fp.write('{}\n'.format(msg))

    if ts:
        print 'total size: {}'.format(ts)
#     gc.collect()
#         if cls == dict and count and count > 1:
#             ds = get_type(cls)
#             def test(ki):
#                 if isinstance(ki, str):
#                     return not ki.startswith('__')
#
#             for di in ds:
#                 ks = (k for k in di.keys() if test(k))
#                 msg = ','.join(ks).strip()
#                 if msg:
#                     print 'keys: {}'.format(msg)


def show_refs(cls):
    obj = next((o for o in gc.get_objects() if type(o) == cls), None)
    if obj:
        print '================= {} referrers ================'.format(cls)
#         print '{} referrers'.format(obj)
        for ri in gc.get_referrers(obj):
            keys = ''
            if isinstance(ri, dict):
                keys = ','.join(ri.keys())

            print '{:<30s} {} {}'.format(str(id(ri)), type(ri), ri, keys)

        print '================== {} referents ================'.format(cls)
#         print '{} referents'.format(obj)
        for ri in gc.get_referents(obj):
            keys = ''
            if isinstance(ri, dict):
                keys = ','.join(ri.keys())

            print '{:<30s} {} {}'.format(str(id(ri)), type(ri), ri, keys)
def get_type(cls):
    return (o for o in gc.get_objects() if type(o) == cls)

def get_size(cls, show=False):
    vs = (sys.getsizeof(o) for o in get_type(cls))
    v = sum(vs) * 1024 ** -2
    if show:
        print '{:<30s} {}'.format(cls, v)
    return v

def count_instances(inst=None, group=None, referrers=False, referents=False, prev=0):
    gc.collect()

    if group:
#         def t(x):
#             try:
#                 return group in x.__class__.__name__
#             except:
#                 pass
        t = lambda x: group in str(type(x))
        n = group
        objs = filter(t, gc.get_objects())

        s = sum(sys.getsizeof(o) for o in objs) * 1024 ** -2
        nn = len(objs)
        print '{:<50s}:{} {} {} {}'.format(n, nn, s, prev, nn - prev)
        return nn

    elif inst:
        t = lambda x: isinstance(x, inst)
        n = str(inst)
        objs = filter(t, gc.get_objects())
        s = sum(sys.getsizeof(o) for o in objs) * 1024 ** -2
        print '{:<50s}:{} {}'.format(n, len(objs), s)

    else:
        objs = gc.get_objects()
        key = lambda x: type(x)
        objs = sorted(objs, key=key)
#         for g, aa in groupby(objs, key=key):
#             d = [sys.getsizeof(ai) for ai in aa]
#             s = sum(d)
#             print '{} {} {}'.format(g, len(d), s)

        xx = [(g, [ai for ai in aa])
                for g, aa in groupby(objs, key=key)]

        xx = [(g, sum([sys.getsizeof(ai) for ai in aa]), len(aa))
              for g, aa in xx]

        for g, s, n in sorted(xx, key=lambda x:x[1]):
            if s > 1000:
                print '{:<50s} {} {}'.format(g, s, n)


    if referrers:
        for obj in objs:
            show_referrers(obj)
    if referents:
        for obj in objs:
            show_referents(obj)

def show_referrers(obj):
    print '============ {} referrers =========='.format(obj)
    for ri in gc.get_referrers(obj):
        print ri

def show_referents(obj):
    print '============ {} referents =========='.format(obj)
    for ri in gc.get_referents(obj):
        print ri



if __name__ == '__main__':
    mem_sort()


