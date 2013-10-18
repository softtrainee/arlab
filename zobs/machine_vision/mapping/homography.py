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

#============= enthought library imports =======================
#============= standard library imports ========================
from numpy import vstack, ones, mean, max, std, diag, dot, zeros, concatenate, sqrt, sum
from numpy import linalg
#============= local library imports  ==========================

def normalize(pts):
    return [row / pts[-1] for row in pts]

def make_homog(pts):
    return vstack((pts, ones((1, pts.shape[1]))))

def _C(fp):
    m = mean(fp[:2], axis=1)
    maxstd = max(std(fp[:2], axis=1)) + 1e-9

    C1 = diag([1 / maxstd, 1 / maxstd, 1])
    C1[0, 2] = -m[0] / maxstd
    C1[1, 2] = -m[1] / maxstd
    fp_new = dot(C1, fp)

    return C1, fp_new

def H_from_points(fp, tp):
    if fp.shape != tp.shape:
        raise RuntimeError('images not same shape')

    C1, fp = _C(fp)
    C2, tp = _C(tp)

    nbr_correspondences = fp.shape[1]
    A = zeros((2 * nbr_correspondences, 9))
    for i in range(nbr_correspondences):
        a = [-fp[0, i], -fp[1, i], -1, 0, 0, 0,
             tp[0, i] * fp[0, i], tp[0, i] * fp[1, i], tp[0, i]]
        b = [0, 0, 0, -fp[0, i], -fp[1, i], -1,
             tp[1, i] * fp[0, i], tp[1, i] * fp[1, i], tp[1, i]]
        A[2 * i] = a
        A[2 * i + 1] = b

    U, S, V = linalg.svd(A)

    H = V[8].reshape((3, 3))

    H = dot(linalg.inv(C2), dot(H, C1))
    return H / H[2, 2]

def Haffine_from_points(fp, tp):
    if fp.shape != tp.shape:
        raise RuntimeError('images not same shape')

    C1, fp_cond = _C(fp)
    C2, tp_cond = _C(tp)

    A = concatenate((fp_cond[:2], tp_cond[:2]), axis=0)
    U, S, V = linalg.svd(A.T)

    tmp = V[:2].T
    B = tmp[:2]
    C = tmp[2:4]

    tmp2 = concatenate((dot(C, linalg.pinv(B)), zeros((2, 1))), axis=1)
    H = vstack((tmp2, [0, 0, 1]))

    H = dot(linalg.inv(C2), dot(H, C1))
    return H / H[2, 2]

def H_from_ransac(fp, tp, model, maxiter=1000, match_threshold=10):
    import ransac
    data = vstack((fp, tp))
    H, ransac_data = ransac.ransac(data.T, model, 4, maxiter, match_threshold, 10, return_all=True)
    return H, ransac_data['inliers']

class RansacModel(object):
    def fit(self, data):
        data = data.T
        fp = data[:3, :4]
        tp = data[3:, :4]
        return H_from_points(fp, tp)

    def get_error(self, data, H):
        data = data.T
        fp = data[:3]
        tp = data[3:]

        fp_tran = dot(H, fp)
        for i in range(3):
            fp_tran[i] /= fp_tran[2]
        return sqrt(sum((tp - fp_tran) ** 2, axis=0))
#============= EOF =============================================
