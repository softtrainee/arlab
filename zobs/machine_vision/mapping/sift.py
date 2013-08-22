# @PydevCodeAnalysisIgnore
#===============================================================================
# Copyright 2012 Jake Ross
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
http://www.janeriksolem.net/2009/02/sift-python-implementation.html
'''
#============= enthought library imports =======================
#============= standard library imports ========================
from PIL import Image
import os
from numpy import loadtxt, array, linalg, zeros, dot, arccos, argsort
#============= local library imports  ==========================

def process_image(imagename, resultname, params="--edge-thresh 10 --peak-thresh 5"):
    """ Process an image and save the results in a file. """

    if imagename[-3:] != 'pgm':
        # create a pgm file
        im = Image.open(imagename).convert('L')
        im.save('tmp.pgm')
        imagename = 'tmp.pgm'

    cmmd = str("sift " + imagename + " --output=" + resultname +
                " " + params)
    os.system(cmmd)
    print 'processed', imagename, 'to', resultname

def read_features_from_file(filename):
    """ Read feature properties and return in matrix form. """

    f = loadtxt(filename)
    return f[:, :4], f[:, 4:]  # feature locations, descriptors

def match(desc1, desc2):
    """ For each descriptor in the first image,
select its match in the second image.
input: desc1 (descriptors for the first image),
desc2 (same for second image). """

    desc1 = array([d / linalg.norm(d) for d in desc1])
    desc2 = array([d / linalg.norm(d) for d in desc2])

    dist_ratio = 0.6
    desc1_size = desc1.shape

    matchscores = zeros((desc1_size[0]), 'int')
    desc2t = desc2.T  # precompute matrix transpose
    for i in range(desc1_size[0]):
        dotprods = dot(desc1[i, :], desc2t)  # vector of dot products
        dotprods = 0.9999 * dotprods
        # inverse cosine and sort, return index for features in second image
        indx = argsort(arccos(dotprods))

        # check if nearest neighbor has angle less than dist_ratio times 2nd
        if arccos(dotprods)[indx[0]] < dist_ratio * arccos(dotprods)[indx[1]]:
            matchscores[i] = int(indx[0])

    return matchscores
#============= EOF =============================================
