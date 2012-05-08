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
        dst = src.clone()

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
    frame = cv.imread(path, 1)
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
def crop(src, x, y, w, h, mat=True):
#    print y, y + h, x, x + w
    v = src[y:y + h, x:x + w]
    if mat:
        v = cv.asMat(v)
    return v
#    return cv.asMat(v)
#    cv.setImageROI(src, new_rect(x, y, w, h))
#    print y, y + h, x, x + w, src.size()
#    return cv.asMat(src[y:y + h, x:x + w])


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

def convert(src, dst):
    cv.convertScaleAbs(src, dst)
    return dst

def accumulate(src, dst):
    cv.accumulate(src, dst)

def running_average(src, dst):
    cv.accumulate(src, dst)


def new_dst(width=640, height=480, depth=3, mode='uint8'):
    dst = cv.asMat(zeros((height, width, depth), mode))
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


def canny(src, t1, t2):
    dst = src.clone()
    cv.Canny(src, dst, t1, t2, 3)
    return dst


def sobel(src, dst, xorder, yorder, aperture=3):
    cv.Sobel(src, dst, 3, xorder, yorder, aperture)
#    draw_rectangle(dst, 10, 10, 50, 50)

    ndst = src.clone()
    cv.convertScaleAbs(dst, ndst)
    cv.bitwise_not(ndst, ndst)
    return ndst


def denoise(src):
    dst = src.clone()

    cv.pyrUp(src, dst)
    cv.pyrDown(dst, src)
#    return src


def smooth(src):
    dst = src.clone()
    cv.smooth(src, dst, cv.CV_BLUR, 3, 3, 0)
    return dst


def get_focus_measure(src, kind):
#    from numpy import r_
#    from scipy import fft
#    from pylab import plot, show
#    w = 100
#    h = 100
#    x = (640 - w) / 2
#    y = (480 - h) / 2
#    src = crop(src, x, y, w, h)
#    src = grayspace(src)
#    d = src.ndarray
#
##    print d[0]
##    print d[-1]
#    fftsig = fft(d)
#    d = abs(fftsig)
#    print d.shape
#    dst = src.clone()
#    cv.convertScaleAbs(cv.asMat(d), dst, 1, 0)
#    return dst

#    xs = xrange(len(ys))
#    plot(xs, ys)
#    show()
#    N = len(d)
#    f = 50000 * r_[0:(N / 2)] / N
#    n = len(f)
##    print f
#    d = d.transpose()
#    d = abs(fftsig[:n]) / N
#    print d
##    plot(f, d[0], 'b', f, d[1], 'g', f, d[2], 'r')
#    plot(f, d)
#    show()

    planes = cv.vector_Mat()
    src = cv.asMat(src)
    laplace = cv.Mat(src.size(), cv.CV_16SC1)
    colorlaplace = cv.Mat(src.size(), cv.CV_8UC3)

    cv.split(src, planes)
    for plane in planes:
        cv.Laplacian(plane, laplace, 3)
        cv.convertScaleAbs(laplace, plane, 1, 0)

    cv.merge(planes, colorlaplace)
    f = colorlaplace.ndarray.flatten()
#    f.sort()
#    print f[-int(len(f) * 0.1):], int(len(f) * 0.1), len(f)
#    len(f)
    return f[-int(len(f) * 0.1):].mean()


def get_frequency_content(src):
    gsrc = grayspace(src)
    dst = src.clone()
    from numpy.fft import fft, fftfreq
    from numpy import abs
    from pylab import plot, show
#    print
    signal = fft(gsrc.ndarray[240])
    ys = abs(signal.real)
    xs = fftfreq(signal.size)
    plot(xs, ys)
    show()

#    signal = cv.asMat(signal.real)
#    cv.convertScaleAbs(signal, dst)
#    return colorspace(dst)
#    print signal.real
    return src


#    print fftfreq(signal.size)
#    dst = cv.Mat(src.size(), cv.CV_32FC1)
#
#    dst1 = cv.asMat(src.ndarray.astype('float32'), cv.CV_32FC1)
#    src.convertTo(dst1, cv.CV_32FC1)
#    print dst1
#    cv.dft(dst1, dst)

#    return colorlaplace

def find_circles(src, min_area):

    c = cv.HoughCircles(src,
                        3,
                        100,
                        60,
                        10,
                        )

    return c


def isolate_color(src, channel):
    planes = cv.vector_Mat()
    cv.split(src, planes)
    w, h = src.size()
    for i in range(3):
        if i == channel:
            continue
        planes[i] = cv.Mat(src.size(), cv.CV_8UC1)

    dst = cv.Mat(src.size(), cv.CV_8UC3)
    cv.merge(planes,
              dst)
    print dst
    return dst


def find_lines(src, t1, minlen=100):
#    dst = canny(src, t1, t2)

    dst = threshold(src, t1, invert=True)
    lines = cv.HoughLinesP(dst, 1, cv.CV_PI / 180, 5, minlen, 20)
#    print lines
    dst = colorspace(dst)
    for l in lines:
        cv.line(dst, new_point(int(l[0]), int(l[1])),
                new_point(int(l[2]), int(l[3])), convert_color((255, 0, 0)),
                3, 8)
    return dst, lines

def get_polygons(contours, hierarchy, min_area=0, max_area=1e10,
                 convextest=True, hole=True, nsizes=5, **kw):
    '''
    '''

    polygons = []
    brs = []
    areas = []

    for cont, hi in zip(contours, hierarchy.tolist()):
        cont = cv.asMat(cont)
#        for i in [0.01]:
        m = cv.arcLength(cont, True)
        result = cv.approxPolyDP_int(cont, m * 0.01, True)
        res_mat = cv.asMat(result)
        area = abs(cv.contourArea(res_mat))

        if hole:
            hole_flag = hi[3] != -1
        else:
            hole_flag = True

#        print cv.isContourConvex(res_mat)
#        print result
#            print 'checking',len(result), area,area>min_area, area<max_area,cv.isContourConvex(res_mat) == bool(convextest), hole_flag 
#            print cv.isContourConvex(res_mat), convextest
        if (len(result) > nsizes
            and area > min_area
            and area < max_area
            #and area < 3e6
#            and cv.isContourConvex(res_mat) == bool(convextest)
            and hole_flag
                ):

            if convextest and not cv.isContourConvex(res_mat):
                continue

            polygons.append(result)
            brs.append(cv.boundingRect(res_mat))
            areas.append(area)
#    print len(polygons), len(contours), area
    return polygons, brs, areas


def add_images(s1, s2):
    dst = s1.clone()
    cv.add(s1, s2, dst)
    return dst


#===============================================================================
# drawing functions
#===============================================================================
def convert_color(color):
    '''
    '''
    if isinstance(color, tuple):
#        color = (color[2], color[1], color[0])
#        color = (color[0], color[1], color[2])
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
                      hole_color=(255, 0, 255),
                      thickness=1
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

        color = hole_color if hi[3] != -1 else external_color
        p = cv.vector_vector_Point2i()
        #if hi[3]
        p.create([ci])
        cv.drawContours(src,
                        p,
#                   clist,
                    - 1,
                   #convert_color(external_color),
                   convert_color(color),
                   #255,
                   thickness=thickness
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


def draw_circle(src, center, radius, color=(255.0, 0, 0), thickness=1):

    if isinstance(center, tuple):
        center = new_point(*center)

    cv.circle(src, center, radius,
              convert_color(color),
#              cv.CV_RGB(255, 0, 0),
              thickness=thickness,
              lineType=cv.CV_AA
              )


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
