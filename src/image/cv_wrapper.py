#===============================================================================
# Copyright 2013 Jake Ross
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
from numpy import array, asarray, ndarray
from collections import namedtuple
from scipy.ndimage.filters import laplace

try:
    from cv2 import VideoCapture, VideoWriter, imwrite, line, fillPoly, polylines, \
        rectangle, imread, findContours, drawContours, arcLength, \
        approxPolyDP, contourArea, isContourConvex, boundingRect, GaussianBlur, addWeighted, \
        circle, moments, minAreaRect, minEnclosingCircle, convexHull

    from cv import ConvertImage, fromarray, LoadImage, Flip, \
        Resize, CreateImage, CvtColor, Scalar, CreateMat, Copy, GetSubRect, PolyLine, Split, \
        Merge, Laplace, ConvertScaleAbs, GetSize

    from cv import CV_CVTIMG_SWAP_RB, CV_8UC1, CV_BGR2GRAY, CV_GRAY2BGR, \
        CV_8UC3, CV_RGB, CV_16UC1, CV_32FC3, CV_CHAIN_APPROX_NONE, CV_RETR_EXTERNAL, \
        CV_AA, CV_16UC3, CV_16SC1
except ImportError, e:
    print e
    print 'OpenCV required'


#============= local library imports  ==========================
from src.geometry.centroid import calculate_centroid


def get_focus_measure(src, kind):
    if isinstance(src, ndarray):
        src = fromarray(src)

    w, h = GetSize(src)
    dst = CreateMat(w, h, CV_16SC1)
    Laplace(src, dst)

    d = asarray(dst).flatten()
    return max(d)

#    planes = CreateMat(3, 1, CV_8UC3)

#    print src
#     if not isinstance(src, ndarray):
#         src = asarray(src)


#     v = laplace(src)
#     return v.flatten().mean()
#
#    w, h = GetSize(src)
# #    src = asMat(src)
#    laplace = CreateMat(w, h, CV_16SC1)
#    colorlaplace = CreateMat(w, h, CV_8UC3)
#
#    Split(src, planes)
#    for plane in planes:
#        Laplace(plane, laplace, 3)
#        ConvertScaleAbs(laplace, plane, 1, 0)
#
#    Merge(planes, colorlaplace)
#    f = asarray(colorlaplace).flatten()
# #    f = colorlaplace.ndarray.flatten()
# #    f.sort()
# #    print f[-int(len(f) * 0.1):], int(len(f) * 0.1), len(f)
# #    len(f)
#    return f[-int(len(f) * 0.1):].mean()

def crop(src, x, y, w, h):


#    cropped = CreateMat(w, h, CV_8UC3)
# #                           (roi_width, roi_height), d, c)
#    rect = map(int, (x, y, w, h))
#    print rect
# #    print (x, y, w, h)
    if not isinstance(src, ndarray):
        src = asarray(src)
#
#    src_region = GetSubRect(src, rect)
#    Copy(src_region, cropped)
#    return cropped
#    return fromarray(src[y:y + h, x:x + w])
    return src[y:y + h, x:x + w].copy()


def save_image(src, path):
    imwrite(path, src)

def colorspace(src, cs=None):
    '''

    '''
    if isinstance(src, ndarray):
        src = fromarray(src)

    if cs is None:
        cs = CV_GRAY2BGR


#    try:
#        ch = src.channels
#        w, h = src.cols, src.rows
#    except AttributeError:
#        try:
#            h, w, ch = src.shape
#        except ValueError:
#            ch = 1
#            h, w = src.shape
#            src = fromarray(src)

#    if src.channels == 1:
#        return merge(src, src)
    dst = CreateMat(src.cols, src.rows, CV_8UC3)
#        dst = cv.Mat(cv.Size(src.cols, src.rows), cv.CV_8UC3)
#        dst = new_dst(src, nchannels=3)

    CvtColor(src, dst, cs)
#    else:
#        dst = src

    return dst

def grayspace(src):
    if isinstance(src, ndarray):
        src = fromarray(src)
#    print src
#    src.step = 92
    if src.channels > 1:
        dst = CreateMat(src.height, src.width, CV_8UC1)
        CvtColor(src, dst, CV_BGR2GRAY)
    else:
        dst = src
    return dst
#   gray = CreateMat(img.height, img.width, CV_8UC1)
#   CvtColor(img, gray, CV_BGR2GRAY)
#   return gray
#    if len(src.shape) == 3:
#        h, w, _ = src.shape
#        dst = CreateMat(h, w, CV_8UC1)
#    if src.channels > 1:
# #        for di in dir(src):
# #            print di
#        dst = CreateMat(src.height, src.width, CV_8UC1)
# #        print dst.type, src.type
# #        dst = cv.Mat(src.size(), cv.CV_8UC1)  # cv.Size(src.cols, src.rows), cv.CV_8UC1)
#        CvtColor(src, dst, CV_BGR2GRAY)
#    else:
#        dst = src
#
#    return dst

def resize(src, w, h, dst=None):

    if isinstance(dst, tuple):
        dst = CreateMat(*dst)

    if isinstance(src, ndarray):
        src = asMat(src)

    if dst is None:
        dst = CreateMat(int(h), int(w), src.type)

    Resize(src, dst)
    return dst

def flip(src, mode):
    Flip(src, src, mode)
    return src

def get_size(src):
    if hasattr(src, 'width'):
        return src.width, src.height
    else:
        h, w = src.shape[:2]
        return w, h

def swap_rb(src):
    try:
        ConvertImage(src, src, CV_CVTIMG_SWAP_RB)
    except TypeError:
        src = fromarray(src)
        ConvertImage(src, src, CV_CVTIMG_SWAP_RB)
    return src

_cv_swap_rb = swap_rb

def asMat(arr):
    return fromarray(arr)

def load_image(p, swap_rb=False):

    img = imread(p)
    if swap_rb:
        img = _cv_swap_rb(img)
    return img

def get_capture_device():
    v = VideoCapture()
    return v

def new_video_writer(path, fps, size):
    fourcc = 'MJPG'
    v = VideoWriter(path, fourcc, fps, size)
    return v

#===============================================================================
# image manipulation
#===============================================================================
def sharpen(src):
    src = asarray(src)
    w, h = get_size(src)
#    w, h = src.size()
#    im = new_dst(w, h)
#    kern = CreateMat(3, 3, src.type)
#    print type(kern), type(src)
    im = GaussianBlur(src,
                      (3, 3), 3)
    addWeighted(src, 1.5, im, -0.5, 0, im)
    return im
#===============================================================================
# drawing
#===============================================================================
_new_point = namedtuple('Point', 'x y')
def new_point(x, y, tt=False):
    x, y = map(int, (x, y))
    if tt:
        return x, y
    else:
        return _new_point(x, y)

#    return Point(x,y)
def convert_color(color):
    if isinstance(color, tuple):
#        color = (color[2], color[1], color[0])
#        color = (color[0], color[1], color[2])
        color = CV_RGB(*color)
    else:
        color = Scalar(color)
    return color

def draw_circle(src, center, radius, color=(255.0, 0, 0), thickness=1):

    if isinstance(center, tuple):
        center = new_point(*center)
    circle(src, center, radius,
              convert_color(color),
              thickness=thickness,
              lineType=CV_AA
              )

def draw_lines(src, lines, color=(255, 0, 0), thickness=3):
    if lines:
        for p1, p2 in lines:
            p1 = new_point(*p1)
            p2 = new_point(*p2)
            line(src, p1, p2,
                   convert_color(color), thickness, 8)

def draw_polygons(img, polygons, thickness=1, color=(0, 255, 0)):
    color = convert_color(color)
#    cv.polylines(img, polygons)
#    p = vector_vector_Point2i()
#    p.create(polygons)

#    print polygons, polygons.shape
    if thickness == -1:
        fillPoly(img, polygons, color)
    else:
        polylines(img, array(polygons, dtype='int32'), 1, color,
                  thickness=thickness
                  )

def draw_rectangle(src, x, y, w, h, color=(255, 0, 0), thickness=1):
    '''
    '''
    p1 = new_point(x, y, tt=True)
    p2 = new_point(x + w, y + h, tt=True)

    rectangle(src, p1, p2, convert_color(color), thickness=thickness)

def draw_contour_list(src, contours, hierarchy, external_color=(0, 255, 255),
                      hole_color=(255, 0, 255),
                      thickness=1):
    n = len(contours)
    for i, _ in enumerate(contours):
        j = i + 1
        drawContours(src, contours, i,
                     convert_color((j * 255 / n, j * 255 / n, 0)), -1
                     )

def get_centroid(pts):
    return calculate_centroid(pts)
#===============================================================================
# segmentation
#===============================================================================
def contour(src):
#    return None, None
#    print src, type(src)
#    nsrc = fromarray(src[:, :])
    return findContours(src, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_NONE)

def get_polygons(src,
                 contours, hierarchy,
                 convextest=False,
#                 hole=False,
                 nsides=5,
                 min_area=100,
                 perimeter_smooth_factor=0.001,
                 **kw):
    polygons = []
#    brs = []
    areas = []
    centroids = []
    min_enclose = []

    for cont in contours:
#    for cont, hi in zip(contours, hierarchy.tolist()):
#        cont = cv.asMat(cont)
#        for i in [0.01]:
        m = arcLength(cont, True)
        result = approxPolyDP(cont, m * perimeter_smooth_factor, True)

#        res_mat = cv.asMat(result)
        area = abs(contourArea(result))
        M = moments(cont)
#        print M['m10'], M['m01'], M['m00']
        if not M['m00']:
            continue
        cent = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])

#        if hole:
#            hole_flag = hi[3] != -1
#        else:
#            hole_flag = True

#        if area > min_area:
#            print 'area', area,
#            print 'hole', hole_flag
#            print 'hi', hi
#            print 'sides', len(result),
#            print 'convext', cv.isContourConvex(res_mat),
#            ch = cv.asMat(cv.convexHull_int(cont))
#            ch = cv.asMat(ch.ndarray.flatten())
#            seq = cv.convexityDefects(cont, ch, cv.createMemStorage(0))
#
#        if not hole_flag:
#            continue

        if not len(result) > nsides:
            continue

        if not area > min_area:
            continue

        if convextest and not isContourConvex(result):
            continue

        a, _, b = cont.shape
        polygons.append(cont.reshape(a, b))
#        ca = contourArea(convexHull(result))
        ca = minEnclosingCircle(result)
        min_enclose.append(ca[1] ** 2 * 3.1415)
#        brs.append(ca)
        areas.append(area)
        centroids.append(cent)

    return polygons, areas, min_enclose, centroids
#============= EOF =============================================
