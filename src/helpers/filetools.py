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



#========== standard library imports ==========
import os

def unique_dir(root, base):
    p = os.path.join(root, '{}001'.format(base))
    i = 2
    while os.path.exists(p):
        p = os.path.join(root, '{}{:03n}'.format(base, i))
        i += 1

    os.mkdir(p)

    return p

def unique_path(root, base, filetype='txt'):
    '''

    '''
    p = os.path.join(root, '%s001.%s' % (base, filetype))
    cnt = 1
    i = 2
    while os.path.exists(p):
        p = os.path.join(root, '%s%03i.%s' % (base, i, filetype))
        i += 1
        cnt += 1

    return p, cnt

def str_to_bool(a):
    '''
    '''

    tks = ['true', 't']
    fks = ['false', 'f']

    tks += [i.capitalize() for i in tks]
    tks += [i.upper() for i in tks]

    fks += [i.capitalize() for i in fks]
    fks += [i.upper() for i in fks]
    if a in tks:
        return True
    elif a in fks:
        return False

def parse_xy(p, delimiter=','):
    '''
    '''
    data = parse_file(p)
    if data:
        func = lambda i, data: [float(l.split(delimiter)[i]) for l in data]

        return func(0, data), func(1, data)

def commented_line(l):
    '''
    '''
    if l[:1] == '#':
        return True
    else:
        return False

def parse_file(p, delimiter=None):
    '''
    '''
    if os.path.exists(p) and os.path.isfile(p):
        with open(p, 'U') as file:
            r = filetoarray(file)
            if delimiter:
                r = [ri.split(delimiter) for ri in r]

            return r


def parse_setupfile(p):
    '''
    '''

    file = parse_file(p)
    if file:
        return [line.split(',') for line in file]

def parse_canvasfile(p, kw):
    '''
    
    '''
    #kw=['origin','valvexy','valvewh','opencolor','closecolor']

    if os.path.exists(p) and os.path.isfile(p):
        with open(p, 'r') as file:
            indices = {}
            i = 0
            f = filetoarray(file)
            count = 1
            for i in range(len(f)):
                if f[i][:1] == '!':
                    for k in kw:
                        if f[i][1:] == k:
                            i += 1
                            if k in indices:
                                k = k + str(count)
                                count += 1

                            indices[k] = f[i].split(',')

                            i += 1
                            break

            return indices
def filetoarray(f, commentchar='#'):
    '''

    '''
    def isNewLine(c):
        return c == chr(10) or c == chr(13)

    r = []

    for line in f:
        cc = line[:1]
        if not cc == commentchar and not isNewLine(cc):
            #l = line[:-1] if line[-1:] == '\n' else line
            #remove inline comments
            line = line.split('#')[0]
            r.append(line.strip())
    return r
