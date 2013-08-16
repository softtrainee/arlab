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
root = os.path.join(os.path.expanduser('~'), 'Desktop', 'memtest')
if not os.path.isdir(root):
    os.mkdir(root)

def write_mem(msg, m):
    p = unique_path(root, 'mem')
    with open(os.path.join(root, p), 'a') as fp:
        fp.write('{:<50s}:{}\n'.format(msg, m))


PID = None
def mem_break():
    write_mem('#' + '=' * 49, '')

def mem_log(msg):
    mem = _get_current_mem()
    write_mem(msg, mem)

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




if __name__ == '__main__':
    mem_sort()


