'''
Copyright 2011 Jake Ross

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
import pyopencv as cv
from numpy import array, ones, zeros
from src.data_processing.centroid.centroid import centroid as _centroid

#
#def clone(src):
#    return cv.cloneMat(src)

#def cvSetImageROI():
#    pass
#def cvResetImageROI():
#    pass
#def subsample(src, x, y, w, h):
#    return cv.asMat(src[x:]
def resize(src, w, h, dst=None):
    if dst is None:
        dst = cv.Mat()
    cv.resize(src, dst, cv.Size(w, h))
    return dst


def asMat(src):
    return cv.asMat(src)


def frompil(src):
    return cv.Mat.from_pil_image(src)

#def setImageROI(*args):
#    return cv.setImageROI(*args)
#
#
#def resetImageROI(*args):
#    return cv.ResetImageROI(*args)


def load_image(path, swap=False):
    '''
    '''
    frame = cv.imread(path)
#    if swap:
#        cv.convertImage(frame, frame, cv.CV_CVTIMG_SWAP_RB)
    return frame


def new_rect(x, y, w, h):
    '''

    '''
    return cv.Rect(x, y, w, h)


def new_point(x, y):
    '''
    '''
#    return cv.Point2d(cvRound(x), cvRound(y))
    return cv.Point2i(cv.round(x), cv.round(y))
#    return cv.Point2d(x, y)


#==============================================================================
# manipulation functions
#==============================================================================
def crop(src, x, y, w, h):
#    cv.setImageROI(src, new_rect(x, y, w, h))
    return cv.asMat(src[y:y + h, x:x + w])


def colorspace(src, cs=None):
    '''

    '''
    if cs is None:
        cs = cv.CV_GRAY2BGR

    if src.channels() == 1:
        dst = cv.Mat(cv.Size(src.cols, src.rows), cv.CV_8UC3)
#        dst = new_dst(src, nchannels=3)
        cv.cvtColor(src, dst, cs)
    else:
        dst = src
    return dst


def grayspace(src):
    '''
    '''
#    dst = cv.Mat(src.size(), cv.CV_8UC1)#cv.Size(src.cols, src.rows), cv.CV_8UC1)
#    cv.cvtColor(src, dst, cv.CV_BGR2GRAY)
    if src.channels() > 1:
        dst = cv.Mat(src.size(), cv.CV_8UC1)#cv.Size(src.cols, src.rows), cv.CV_8UC1)
        cv.cvtColor(src, dst, cv.CV_BGR2GRAY)
    else:
        dst = src

    return dst


def threshold(src, threshold, invert=False):
    '''
    '''
    dst = src.clone()
    kind = cv.THRESH_BINARY
    if invert:
        kind = cv.THRESH_BINARY_INV

    cv.threshold(src, dst, threshold, 255, kind)

    return dst


def swapRB(src):
    dst = src.clone()
    cv.convertImage(src, dst, cv.CV_CVTIMG_SWAP_RB)
    return dst

#def new_dst(src, width=None, height=None, a=None, b=None):
#    return src.clone()


#def new_color_dst(width, height, zero=True):
#    dst = cv.Mat(cv.Size(width, height), cv.CV_8UC3)
#    if zero:
#        zeros((width, height, 3))
#
#    return dst

def new_dst(width, height, depth):
    dst = cv.asMat(zeros((width, height, depth), 'uint8'))
    return dst

def add_scalar(src, v):
    if isinstance(v, int):
        v = (v,) * src.channels()

    cv.add(src, cv.Scalar(*v), src)

#def zero(src):
#    cv.zero(src)
#===============================================================================
# morphology
#===============================================================================
def erode(src, ev):
    '''

    '''
    dst = src.clone()
    element = _get_morphology_element(ev)
    cv.erode(src, dst, element)
    return dst


def dilate(src, dv):
    '''
    '''
    dst = src.clone()
    element = _get_morphology_element(dv)
    cv.dilate(src, dst, element)
    return dst


def _get_morphology_element(v):
    return cv.asMat(ones((v * 2 + 1, v * 2 + 1), 'uint8'), True)


#==============================================================================
# calculation functions
#==============================================================================
def centroid(polypts):

    pts = array([(pt.x, pt.y) for pt in polypts], dtype=float)
    return _centroid(pts)


def contour(src):
    '''
    '''
#    c, h = cv.findContours(src.clone(), cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
    c, h = cv.findContours(src.clone(), cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)

    return c, h


def get_polygons(contours, hierarchy, min_area=0, max_area=1e10,
                 convextest=True, hole=True):
    '''
    '''

    polygons = []
    brs = []
    for cont, hi in zip(contours, hierarchy.tolist()):
        cont = cv.asMat(cont)
#        for i in [0.01, 0.02, 0.04]:
        for i in [0.06]:
            m = cv.arcLength(cont, True)
            result = cv.approxPolyDP_int(cont, m * 0.01, True
                                         #cv.arcLength(cont, False),
                                         #cv.arcLength(cont, False) * i,
                                         #False
                                         )
            res_mat = cv.asMat(result)
            area = abs(cv.contourArea(res_mat))

            if hole:
                hole_flag = hi[3] != -1
            else:
                hole_flag = True

#            print cv.isContourConvex(res_mat), convextest
            if (len(result) > 5
                and area > min_area
                and area < max_area
                #and area < 3e6
                and cv.isContourConvex(res_mat) == bool(convextest)
                and hole_flag
                    ):

                polygons.append(result)
                brs.append(cv.boundingRect(res_mat))

#    print len(polygons), len(contours), area
    return polygons, brs


#===============================================================================
# drawing functions
#===============================================================================
def convert_color(color):
    '''
    '''
    if isinstance(color, tuple):
#        color = (color[2], color[1], color[0])
        color = (color[0], color[1], color[2])
        color = cv.CV_RGB(*color)
    else:
        color = cv.Scalar(color)
    return color


def draw_point(src, pt, color=(255, 0, 0), thickness= -1):
    '''
    '''
    if isinstance(pt, (tuple, list)):
#        pt = [int(pi for pi in pt]
        pt = cv.Point2d(*pt)

    color = convert_color(color)
    cv.circle(src, pt, 5, color, thickness=thickness)


def draw_polygons(img, polygons, thickness=1, color=(0, 255, 0)):
    '''
    '''
    color = convert_color(color)
#    cv.polylines(img, polygons)
    p = cv.vector_vector_Point2i()
    p.create(polygons)
    cv.polylines(img, p, 1, color, thickness=thickness)
#    for pa in polygons:
#        if thickness == -1:
#            cv.fillPoly(img, [pa], color)
#        else:
#            cv.polylines(img, cv.vector_vector_Point2d.create([pa]), 1, color, thickness=thickness)


def draw_contour_list(src, clist, hierarchy=None,
                       external_color=(0, 0, 255),
                      hole_color=(255, 255, 0)
                      ):
    '''
    '''
#    print 'ncont', len(clist)
#    p = cv.vector_vector_Point2i()
#    p.create(clist)
#    for ci in clist:

#        p.cre
#    print 'hi', hierarchy
    if hierarchy is None:
        hierarchy = [[True] * 4] * len(clist)

    for hi, ci in zip(hierarchy, clist):
        p = cv.vector_vector_Point2i()
        #if hi[3]
        p.create([ci])
        cv.drawContours(src,
                        p,
#                   clist,
                    - 1,
                   #convert_color(external_color),
                   convert_color(hole_color),
                   #255,
                   thickness=1
                   )


def draw_lines(src, lines, color=(255, 0, 0), thickness=3):
    if lines:
        for p1, p2 in lines:
            p1 = new_point(*p1)
            p2 = new_point(*p2)
            cv.line(src, p1, p2,
                   convert_color(color), thickness, 8)


def draw_rectangle(src, x, y, w, h, color=(255, 0, 0), thickness=1):
    '''
    '''
    p1 = new_point(x, y)
    p2 = new_point(x + w, y + h)
    cv.rectangle(src, p1, p2, convert_color(color), thickness=thickness)


def draw_circle(src, center, radius, color=(255, 0, 0), thickness=1):
    cv.circle(src, center, radius, convert_color(color), thickness=thickness, line_type=cv.CV_AA)


def cvFlip(src, mode):
    cv.flip(src, src, mode)


#===============================================================================
# video 
#===============================================================================
def get_capture_device(deviceid):
    return cv.VideoCapture(deviceid)


def query_frame(device):
    frame = cv.Mat()
    device >> frame
#    dst = cv.Mat()
    dst = frame
    #resize(frame, dst, 640, 480)
#    print frame.size()
    return dst


def write_frame(writer, src):
    writer << src


def new_video_writer(path, fps, size):
    return cv.VideoWriter(path, cv.CV_FOURCC('D', 'I', 'V', 'X'),
                          fps, cv.Size(*size), True)


def get_fps(cap):
    return cap.get(cv.CV_CAP_PROP_FPS)


def save_image(src, path):
    cv.imwrite(path, src)

if __name__ == '__main__':
    cv.namedWindow('foo', 1)
#    src = load_image('/Users/ross/Programming/demo/lena.jpg', swap=True)
    src = load_image('/Users/ross/Programming/demo/lena.jpg', swap=True)
#    draw_point(src, (100, 100))
    gsrc = grayspace(src)
    tsrc = threshold(gsrc, 100)
    csrc = colorspace(tsrc)
#    gsrc = src
#    conts, hierarchy = contour(tsrc)
##
#    print get_polygons(conts)

    draw_lines(csrc, [[(0, 0), (100, 100)]])
    cv.imshow('foo', csrc)
    c = cv.waitKey(0)
#    if(c & 255 == 27):
#        break
#======== EOF ===================================================
#def new_dst(src, zero=False, width=None,
#            height=None, nchannels=None, size=None):
#    '''
#    '''
#
##    print nchannels
#    if width is not None and height is not None:
#        size = cv.Size(width, height)
#    elif size is None:
#        size = cv.getSize(src)
#
#    if nchannels is None:
#        nchannels = src.nChannels
#
#    img = cv.createImage(size, 8, nchannels)
#    if zero:
#        cv.zero(img)
#    return img
