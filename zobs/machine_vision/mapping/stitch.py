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

#============= enthought library imports =======================
#============= standard library imports ========================
from numpy import array, dot
import os
from PIL import Image
#============= local library imports  ==========================
import sift
import homography
from warping import horizontal_panorama

def find_matches(image_names, root):
    l = {}
    d = {}
    n = len(image_names)
    for i, im in enumerate(image_names):
        resultname = os.path.join(root, '{}.sift'.format(im))
        if not os.path.isfile(resultname):
            sift.process_image(os.path.join(root, '{}.png'.format(im)), resultname)
        l[i], d[i] = sift.read_features_from_file(resultname)

    matches = {}
    for i in range(n - 1):
        matches[i] = sift.match(d[i + 1], d[i])
    return matches, l, d

def convert_points(matches, l, j):
    ndx = matches[j].nonzero()[0]
    fp = homography.make_homog(l[j + 1][ndx, :2].T)
    ndx2 = [int(matches[j][i]) for i in ndx]
    tp = homography.make_homog(l[j][ndx2, :2].T)

    return fp, tp

def open_image(root, name):
    return array(Image.open(os.path.join(root, '{}.png'.format(name))))

def hor_stitch(root, image_names, result_name='result'):
    matches, l, d = find_matches(image_names, root)
    model = homography.RansacModel()

#    fp, tp = convert_points(matches, l, 2)
#    H_32 = homography.H_from_ransac(fp, tp, model)[0]
#
#    fp, tp = convert_points(matches, l, 3)
#    H_43 = homography.H_from_ransac(fp, tp, model)[0]

    delta = 2000
    center_idx = 2
    end = 4
#    im1 = array(Image.open(image_names[center_idx - 1]))
#    im2 = array(Image.open(image_names[center_idx]))
    im1 = open_image(root, image_names[center_idx - 1])
    im2 = open_image(root, image_names[center_idx])
    fp, tp = convert_points(matches, l, center_idx - 1)
    prev_H = homography.H_from_ransac(fp, tp, model)[0]
    pano = horizontal_panorama(prev_H, im1, im2, delta, delta)

    for i in range(center_idx - 1, 0, -1):
        fp, tp = convert_points(matches, l, center_idx - 1 - i)
        Ha = homography.H_from_ransac(fp, tp, model)[0]
        H = dot(prev_H, Ha)
        im1 = open_image(root, image_names[center_idx - 1 - i])
#        im1 = array(Image.open(image_names[center_idx - 1 - i]))
        pano = horizontal_panorama(H, im1, pano, delta, delta)
        prev_H = Ha

#    im2 = array(Image.open(image_names[center_idx + 1]))
    im2 = open_image(root, image_names[center_idx + 1])
    tp, fp = convert_points(matches, l, center_idx)  # reverse order
    prev_H = homography.H_from_ransac(fp, tp, model)[0]
    pano = horizontal_panorama(prev_H, im1, im2, delta, delta)
    for i in range(center_idx, end, 1):
        tp, fp = convert_points(matches, l, center_idx + 1 + i)
        Ha = homography.H_from_ransac(fp, tp, model)[0]
        H = dot(prev_H, Ha)
        im1 = open_image(root, image_names[center_idx + 1 + i])
        pano = horizontal_panorama(H, im1, pano, delta, delta)
        prev_H = Ha

    pano = Image.fromarray(pano)
    pano.save(os.path.join(root, '{}.png'.format(result_name)))


#    fp, tp = convert_points(matches, l, center_idx - 2)
#    H_01 = homography.H_from_ransac(fp, tp, model)[0]
#
#    im = array(Image.open(image_names[center_idx - 2]))
#    pano = warping.panorama_v(dot(H_12, H_01), im, pano, delta, delta)
#
#    H_01 = homography.H_from_ransac(fp, tp, model)[0]
#
#    im = array(Image.open(image_names[center_idx + 1]))
#    pano = warping.panorama_v(dot(H_12, H_01), im, pano, delta, delta)


#    im = array(Image.open(image_names[3]))
#    pano = warping.panorama_v(, im, pano, delta, delta)


#============= EOF =============================================
