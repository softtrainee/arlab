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



'''
Color generator methods
utility functions for creating a series of colors
'''
#colors8i = dict(black = (0, 0, 0),
#                green = (0, 255, 0),
#                blue = (0, 0, 255),
#                yellow = (255, 255, 0),
#                red = (255, 0, 0),
#                purple = (0, 255, 255),
#                deepskyblue = (0, 191, 255),
#                gray = (125, 125, 125),
#                orange = (255, 140, 0),
#                lightgreen = (50, 205, 50),
#                pink = (255, 20, 147),
#                silver = (84, 84, 84)
#                )

colors8i = dict(
                black=(0, 0, 0),
                red=(255, 0, 0),
                maroon=(127, 0, 0),
                yellow=(255, 255, 0),
                olive=(127, 127, 0),
                lime=(0, 255, 0),
                green=(0, 127, 0),
                gray=(127, 127, 127),
                aqua=(0, 255, 255),
                teal=(0, 127, 127),
                blue=(0, 0, 255),
                silver=(191, 191, 191),
                navy=(0, 0, 127),
                fuchsia=(255, 0, 255),
                purple=(127, 0, 127)

              )
colors1f = dict()
for color in colors8i:
    c = colors8i[color]
    colors1f[color] = c[0] / 255., c[1] / 255., c[2] / 255.
colornames = [ 'black', 'red', 'maroon', 'yellow', 'olive',
               'lime', 'gray', 'green', 'aqua', 'teal',
               'blue', 'silver', 'navy', 'fuchsia', 'purple']
def colorname_generator():
    '''
    '''
    i = 0
    while 1:
        if i == len(colornames):
            i = 0
        yield colornames[i]
        i += 1


def color8i_generator():
    '''
    '''
    i = 0
    while 1:
        if i > len(colornames):
            i = 0
        yield colors8i[colornames[i]]
        i += 1

def color1f_generator():
    '''
    '''
    i = 0
    while 1:
        if i > len(colornames):
            i = 0
        yield colors1f[colornames[i]]
        i += 1
