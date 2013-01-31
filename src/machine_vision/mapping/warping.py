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
from numpy import array, dot, hstack, zeros
from src.machine_vision.mapping import homography
from scipy import ndimage
#============= standard library imports ========================
#============= local library imports  ==========================

def image_in_image(im1, im2, tp):
    '''
    Put im1 in im2 with an affine transformation
    such that corners are as close to tp as possible.
    tp are homogeneous and counter-clockwise from top left.
    '''
    m, n = im1.shape[:2]
    fp = array([[0, m, m, 0], [0, 0, n, n], [1, 1, 1, 1]])

    H = homography.Haffine_from_points(tp, fp)
    im1_t = ndimage.affine_transform(im1, H[:2, :2], (H[0, 2], H[1, 2]), im2.shape[:2])
    alpha = im1_t > 0
    return (1 - alpha) * im2 + alpha * im1_t

def horizontal_panorama(H, fromim, toim, padding=2400, delta=2400):
    '''
    Create horizontal panorama by blending two images
    using a homography H (preferably estimated using RANSAC).
    The result is an image with the same height as toim. 
    padding specifies number of fill pixels and delta additional translation.
    '''

    is_color = len(fromim.shape) == 3
    size = (toim.shape[0], toim.shape[1] + padding)
    def transf(p):
        p2 = dot(H, [p[0], p[1], 1])
        return [p2[0] / p2[2], p2[1] / p2[2]]
    if H[1, 2] < 0: #fromim is to the right
        if is_color:
            toim_t = hstack((toim, zeros((toim.shape[0], padding, 3))))
            fromim_t = zeros((toim.shape[0], toim.shape[1] + padding, toim.shape[2]))
            for col in range(3):
                fromim_t[:, :, col] = ndimage.geometric_transform(fromim[:, :, col],
                                                                  transf, 
#                                                                  output_shape=size
                                                                  )
        else:
            toim_t = hstack((toim, zeros((toim.shape[0], padding))))
            fromim_t = ndimage.geometric_transform(fromim, transf, 
#                                                   output_shape=size
                                                   )
    else:
        if is_color:
            toim_t = hstack((zeros((toim.shape[0], padding, 3)), toim))
            fromim_t = zeros((toim.shape[0], toim.shape[1] + padding, toim.shape[2]))
            for col in range(3):
                fromim_t[:, :, col] = ndimage.geometric_transform(fromim[:, :, col],
                                                                  transf, 
#                                                                  output_shape=size
                                                                  )
        else:
            toim_t = hstack((zeros((toim.shape[0], padding)), toim))
            fromim_t = ndimage.geometric_transform(fromim, transf, 
#                                                   output_shape=size
                                                   )

    if is_color:
        alpha = ((fromim_t[:, :, 0] * fromim_t[:, :, 1] * fromim_t[:, :, 2]) > 0)
        for col in range(3):
            toim_t[:, :, col] = fromim_t[:, :, col] * alpha + toim_t[:, :, col] * (1 - alpha)
    else:
        alpha = (fromim_t > 0)
        toim_t = fromim_t * alpha + toim_t * (1 - alpha)

    return toim_t

#============= EOF =============================================
