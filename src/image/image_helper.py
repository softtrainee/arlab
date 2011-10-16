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
#=============enthought library imports=======================
#=============standard library imports ========================

from thread import start_new_thread
from numpy import array
#=============local library imports  ==========================

from ctypes_opencv import cvErode, cvDilate, cvGetSubRect, cvCreateMat, \
    cvWarpAffine, cv2DRotationMatrix, cvAvg, cvAvgSdv, cvMinMaxLoc, cvZero, cvPolyLine, cvLoadImage, \
    cvConvertImage, cvSaveImage, cvDrawContours, cvFindContours, cvThreshold, cvSubS, cvCheckContourConvexity, \
    cvCalcBackProject, cvCalcHist, cvCreateHist, \
    cvEqualizeHist, cvCopy, cvSetImageCOI, cvSetImageROI, cvNot, \
    cvCanny, cvHoughLines2, cvGetSize, cvCvtColor, cvCloneImage, cvCreateImage, cvLine, \
    cvCreateMemStorage, \
    cvRectangle, cvCircle, \
    cvGetSeqElem, cvCreateSeq, cvApproxPoly, cvContourPerimeter, cvContourArea, \
    CvPoint, CvPoint2D32f, CvRect, CvSize, CvScalar, CvSeq, CvContour, \
    CV_GRAY2BGR, CV_BGR2GRAY, CV_HOUGH_PROBABILISTIC, CV_PI, CV_RGB, \
    CV_8UC3, CV_8UC1, CV_HIST_ARRAY, CV_THRESH_BINARY_INV, CV_THRESH_BINARY, CV_CVTIMG_SWAP_RB, CV_AA, CV_POLY_APPROX_DP, \
    sizeof, \
    cvCreateVideoWriter, CV_FOURCC
    #unused
#    cvClearMemStorage,\
#    cvSet, cvSet2D, cvFilter2D, cvScalarAll, CV_32FC1, cvGet1D, cvSet1D, \
#    CV_HOUGH_STANDARD,cvBoundingRect
    

from ctypes import POINTER
from ctypes_opencv.cv import cvHoughCircles, CV_HOUGH_GRADIENT, CvVect32f, \
    cvFitEllipse2, cvCreateStructuringElementEx, CV_SHAPE_RECT, CV_RETR_CCOMP, \
    CV_RETR_TREE, cvFilter2D
from ctypes_opencv.cxcore import cvCvtSeqToArray, CV_32SC2, CV_32FC2, cvConvert, \
    CvBox2D, cvRound, CV_WHOLE_SEQ_END_INDEX, cvSlice, CV_SEQ_FLAG_HOLE, \
    CV_32FC1, cvScalarAll, cvSet, cvSet2D, cvConvertScale, cvReleaseData, \
    cvGet1D, cvSet1D, cvFillPoly
from src.data_processing.centroid.centroid import centroid as _centroid
from threading import Thread


def convert_seq(seq):
    s = seq.asarrayptr(POINTER(CvPoint))
    return [si.contents for si in s]


storage = cvCreateMemStorage(0)
def centroid(polypts):
    
    pts = array([(pt.x, pt.y) for pt in polypts], dtype=float)
    return _centroid(pts)

#    c = circles.asarrayptr(POINTER(CvScalar))
#    print circles.total
#    for i in range(circles.total):
#        print cvGetSeqElem(circles, i)


def lines(src, thresh=0):
    '''
    '''

#    this is a hack
#    using cvGetSize or using a size equivalent to src.size
#    causes the lines to be drawn on top of the color source
#    simply adding 1 to dimensions seems to fix the problem
#    w=src.width+1
#    h=src.height+1

#    dst=cvCreateImage(CvSize(w,h),8,3)

    dst = new_dst(src,
               # width = src.width + 1,
                #height = src.height + 1,
                nchannels=3,
                zero=True
                )

    lines = cvHoughLines2(src, storage, CV_HOUGH_PROBABILISTIC, 1, CV_PI / 180, int(thresh), 100, 100)
#    lines = cvHoughLines2(src, storage, CV_HOUGH_STANDARD, 1, CV_PI / 180, int(thresh))#, 50, 10)
    lines = lines.asarrayptr(POINTER(CvPoint))
    for line in lines:
        cvLine(dst, line[0], line[1], CV_RGB(255, 0, 0), 3, 8)

    return dst, lines

def crop(src, x, y, w, h):
#    dst = new_dst(src, width = src.width + 1,
#                height = src.height + 1,
#                nchannels = 3)
    cvSetImageROI(src, new_rect(x, y, w, h))
#    cvCopy(src, dst)
#    return dst
def subsample(src, x, y, width, height):
    '''
    '''
    rect = CvRect(x, y, width, height)

    if src.nChannels == 3:
        type = CV_8UC3
    else:
        type = CV_8UC1
    subrect = cvCreateMat(width, height, type)

    cvGetSubRect(clone(src), subrect, rect)
    return subrect
#def subsample(src,width=640,height=480,center=None, add_rect=False):
#    
#    dst=cvCreateImage(CvSize(int(width),int(height)),src.depth,src.nChannels)
#    size=cvGetSize(src)
#    
#    if center is None:
#        x=size.width/2
#        y=size.height/2
#        center=(x,y)
#        
#    center32f=CvPoint2D32f(*center)
#    
#    cvGetRectSubPix(src,dst,center32f)
#    
#    if add_rect:
#        x1=int(center[0]-width/2)
#        y1=int(center[1]-height/2)
#        x2=int(center[0]+width/2)
#        y2=int(center[1]+height/2)
#        cvRectangle(src,CvPoint(x1,y1),CvPoint(x2,y2),
#                    CV_RGB(255,0,0),thickness=4)    
#    return dst

def equalize(src):
    '''
    '''
    dst = new_dst(src)
    cvEqualizeHist(src, dst)
    return dst

def histogram(src):
    '''
    '''
    size = (30, 32)
    type = CV_HIST_ARRAY
    hist = cvCreateHist(size, type)

    h_plane = cvCreateImage(cvGetSize(src), src.depth, 1)
    s_plane = cvCreateImage(cvGetSize(src), src.depth, 1)
    #v_plane = cvCreateImage(cvGetSize(src), src.depth, 1)
#    
    for chan, plane in [(1, h_plane), (2, s_plane)]:
        cvSetImageCOI(src, chan)
        cvCopy(src, plane)

    cvSetImageCOI(src, 0)
    planes = (h_plane, s_plane)
#    
    cvCalcHist(planes, hist, 0, 0)
    dst = new_dst(src, nchannels=1)
    cvCalcBackProject(planes, dst, hist)
    return dst

def colorspace1D(src, channel='r'):
    '''

    '''

    dst = cvCloneImage(src)
    c = 255
    if channel == 'r':
        s = CvScalar(c, c, 0)
    elif channel == 'g':
        s = CvScalar(c, 0, c)
    else:
        s = CvScalar(0, c, c)

    cvSubS(src, s, dst)
    return dst


def get_polygons(contours, min_area=0, max_area=1e10, convextest=0, hole=True):
    '''
    '''

    polygons = []
#    br = None
#    bra = 0
    for i, cont in enumerate(contours.hrange()):
        
        result = cvApproxPoly(cont, sizeof(CvContour),
                     storage, CV_POLY_APPROX_DP,
                     cvContourPerimeter(cont) * 0.001,
                      0)
        
        area = abs(cvContourArea(result))
        #print result.total, area, cvCheckContourConvexity(result), cont.flags
        
        if hole:
            hole_flag = cont.flags & CV_SEQ_FLAG_HOLE != 0
        else:
            hole_flag = cont.flags & CV_SEQ_FLAG_HOLE == 0
            
        if (result.total >= 4
            and area > min_area
            and area < max_area
            #and area < 3e6
            and cvCheckContourConvexity(result) == convextest
            and hole_flag
                ):

            ra = result.asarray(CvPoint)
            polygons.append(new_seq([ra[i] for i in range(result.total)]))



    return [p.asarray(CvPoint) for p in polygons] #, br

def convert_color(color):
    '''
    '''
    if isinstance(color, tuple):
        color = (color[2], color[1], color[0])
        color = CV_RGB(*color)
    else:
        color = CvScalar(color)
    return color

def draw_point(src, pt, color=(255, 0, 0), thickness= -1):
    '''
    '''
    if isinstance(pt, (tuple, list)):
        pt = [int(pi) for pi in pt]
        pt = CvPoint(*pt)

    color = convert_color(color)
    cvCircle(src, pt, 5, color, thickness=thickness)

def draw_polygons(img, polygons, thickness=1, color=(0, 255, 0)):
    '''
    '''
    color = convert_color(color)
    for pa in polygons:
        if thickness == -1:
            cvFillPoly(img, [pa], color)
        else:    
            cvPolyLine(img, [pa], 1, color, thickness=thickness)    

def draw_contour_list(src, clist, external_color=(255, 0, 0),
                      hole_color=(255, 0, 255)
                      ):
    '''
    '''

    cvDrawContours(src,
                   clist,
                   convert_color(external_color),
                   convert_color(hole_color),
                   
#                   CV_RGB(255, 0, 0),
#                   CV_RGB(255, 0, 255),
                   255,
                   thickness=1
                   )

#    for p in polygons:
#        pa = p.asarray(CvPoint)
#        print pa
#        cvPolyLine(src, [pa], 0, CV_RGB(0, 255, 0), 3, CV_AA, 0)
def draw_rectangle(src, x, y, w, h, color=(255, 0, 0), fill=False, thickness=3):
    '''
        
    '''
    if fill:
        thickness = -1

    color = convert_color(color)
    
    p1 = new_point(x, y)
    p2 = new_point(x + w, y + h)
    cvRectangle(src, p1, p2, color, thickness=thickness)

def draw_squares(img, squares):
    '''

    '''
    dst = cvCloneImage(img)
    # read 4 sequence elements at a time (all vertices of a square)
    i = 0
    sqr_arr = squares.asarray(CvPoint)
    pts = []
    while i < squares.total:
        pt = []
        # read 4 vertices
        pt.append(sqr_arr[i])
        pt.append(sqr_arr[i + 1])
        pt.append(sqr_arr[i + 2])
        pt.append(sqr_arr[i + 3])

        # draw the square as a closed polyline
        cvPolyLine(dst, [pt], 1, CV_RGB(0, 255, 0), 3, CV_AA, 0);
        i += 4
        pts.append(pt)

    return dst, pts
def new_video_writer(path, fps=None, frame_size=None):
    '''
    '''
    if fps is None or fps == 0:
        fps = 5
    if frame_size is None:
        frame_size = (640, 480)

    w = cvCreateVideoWriter(path,
                         # CV_FOURCC('P','I','M','1'),
                          CV_FOURCC('X', 'v', 'i', 'D'),
                          fps,
                          CvSize(*frame_size),
                          True
                          )

    return w
def new_mask(src, x, y, w, h):
    '''

    '''
    dst = new_dst(src, nchannels=1)
    cvZero(dst)

    draw_rectangle(dst, CvPoint(x, y), CvPoint(x + w, y + h), color=1, fill=True)
    return dst

def new_rect(x, y, w, h):
    '''

    '''
    return CvRect(x, y, w, h)

def new_point(x, y):
    '''
    '''
    return CvPoint(x, y)

def new_size(src):
    '''
    '''

    return CvSize(src.width & -2,
                  src.height & -2)

def new_seq(data=None):
    '''
    '''

    seq = cvCreateSeq(0, sizeof(CvSeq), sizeof(CvPoint), storage)
    if data is not None:
        for d in data:
            seq.append(d)
    return seq

def new_dst(src, zero=False, width=None, height=None, nchannels=None, size=None):
    '''
    '''


    if width is not None and height is not None:
        size = CvSize(width, height)
    elif size is None:
        size = cvGetSize(src)

    if nchannels is None:
        nchannels = src.nChannels

    img = cvCreateImage(size, 8, nchannels)
    if zero:
        cvZero(img)
    return img

def rotate(src, angle):
    '''
        @type angle: C{str}
        @param angle:
    '''
    center = CvPoint2D32f(src.width / 2, src.height / 2)
    rot_mat = cv2DRotationMatrix(center, angle, 1)
    dst = clone(src)
    cvWarpAffine(src, dst, rot_mat)
    return dst

def clone(src):
    '''
    '''
    return cvCloneImage(src)

def avg(src):
    '''
    '''
    return cvAvg(src)

def avg_std(src):
    '''
    '''
    mean = CvScalar()
    std_dev = CvScalar()
    cvAvgSdv(src, mean, std_dev)
    return mean, std_dev

def get_min_max_location(src, region):
    '''

    '''

    minpt = CvPoint()
    maxpt = CvPoint()
    minval, maxval = cvMinMaxLoc(grayspace(src),
                #minval,maxval,
                               min_loc=minpt,
                               max_loc=maxpt,
                               mask=region
                       )
    return minval, maxval, minpt, maxpt

def erode(src, ev):
    '''

    '''
    e = new_dst(src)
#    mat = cvCreateMat(3, 3, 1)
    kernel = cvCreateStructuringElementEx(3, 3, 0, 0, CV_SHAPE_RECT)
    cvErode(src, e, kernel, int(ev))
    return e

def dilate(src, dv):
    '''
    '''
    d = clone(src)
    cvDilate(d, d, 0, dv)
    return d

def sharpen(src):
    pass
#    gray = grayspace(src)
#    lapl = grayspace(src)
#    
##    print lapl.width, lapl.height
##    print gray.width, gray.height
#    
#    kernel = cvCreateMat(3, 3, CV_8UC1)
#    cvSet(kernel, cvScalarAll(-1.0))
#    cvSet2D(kernel, 1, 1, cvScalarAll(1.0))
##    
#    cvFilter2D(gray, lapl, kernel)
#    
#    minv, maxv = cvMinMaxLoc(lapl)
#    print maxv
#    for i in xrange(0, lapl.width * lapl.height - 1):
#        lapv = cvGet1D(lapl, i).val
#        v = 255 * lapv[0] / maxv
        #cvSet1D(src, i, cvScalarAll(v))
##        
#    minv, maxv = cvMinMaxLoc(gray)
#    for i in xrange(0, lapl.width * lapl.height):
#        lapv = cvGet1D(gray, i).val
#        v = 255 * lapv[0] / maxv
#        cvSet1D(src, i, cvScalarAll(v))
        
def contour(src):
    '''
    '''

    tsrc = clone(src)
    return cvFindContours(tsrc, storage)

def canny(src, lt, ht):
    '''

    '''

    if src.nChannels > 1:
        gsrc = grayspace(src)
    else:
        gsrc = src

    #use canny for edge detection
    dst = new_dst(gsrc, nchannels=1)

    cvCanny(gsrc, dst, lt, ht, 3)

    return dst

def threshold(src, threshold, invert=False):
    '''
    '''
    dst = cvCloneImage(src)
    kind = CV_THRESH_BINARY
    if invert:
        kind = CV_THRESH_BINARY_INV
    
    cvThreshold(src, dst, threshold, 255, kind)

    return dst

def colorspace(src, cs=CV_GRAY2BGR):
    '''

    '''
    if src.nChannels == 1:
        #csrc=cvCreateImage(cvGetSize(src),8,3)
        dst = new_dst(src, nchannels=3)
        cvCvtColor(src, dst, cs)
    else:
        dst = src
    return dst

def grayspace(src):#, width = None, height = None):
    '''
    '''
    if src.nChannels > 1:
        #gsrc=cvCreateImage(cvGetSize(src),8,1)
        dst = new_dst(src, nchannels=1)
        
#        print src.width, dst.width, src.height, dst.height
#        print src
#        print dst
        cvCvtColor(src, dst, CV_BGR2GRAY)
    else:
        dst = src
    #dst2 = new_dst(dst)
    #cvNot(dst, dst2)
    #return dst2
    return dst

def load_image(path, swap=False):
    '''
    '''
    frame = cvLoadImage(path)

    if swap:
        cvConvertImage(frame, frame, CV_CVTIMG_SWAP_RB)
    return frame

def save_image(src, path):
    '''

    '''
    #frame=self.get_frame(flag=CV_CVTIMG_SWAP_RB)
#    cvConvertImage(src, src, CV_CVTIMG_SWAP_RB)
    def _record_frame():
        cvSaveImage(path, src)

    t = Thread(target=_record_frame)
    t.start()
    #start_new_thread(_record_frame, ())
    #return path
#===========#def angle( pt1, pt2, pt0 ):
#    dx1 = pt1.x - pt0.x;
#    dy1 = pt1.y - pt0.y;
#    dx2 = pt2.x - pt0.x;
#    dy2 = pt2.y - pt0.y;
#    return (dx1*dx2 + dy1*dy2)/sqrt((dx1*dx1 + dy1*dy1)*(dx2*dx2 + dy2*dy2) + 1e-10);
#    

#============================ EOF =================
#def find_ellipses(src, contours):
#    centers = []
#    for c in contours.hrange():
#        n = c.total
#        if n < 6:
#            continue
#        pointarray = cvCreateMat(1, n, CV_32SC2)
#        pointarray2d32f = cvCreateMat(1, n, CV_32FC2)
#        cvCvtSeqToArray(c, pointarray.data.ptr, cvSlice(0, CV_WHOLE_SEQ_END_INDEX))
#        cvConvert(pointarray, pointarray2d32f)
#        
#        box = CvBox2D()
#        box = cvFitEllipse2(pointarray2d32f)
#        
#        w = cvRound(box.size.width / 2.0)
#        h = cvRound(box.size.height / 2.0)
#        
#        cx = cvRound(box.center.x)
#        cy = cvRound(box.center.y)
#        centers.append((cx, cy))
##        draw_rectangle(src, CvPoint(cx - w, cy - h),
##                       CvPoint(cx + w, cy + h),
##                       #color=(0, 100, 200)
##                       )
#        
#        
#    return centers
#         
#def find_circles(src):
#    gsrc = grayspace(src)
#    
#    circles = cvHoughCircles(gsrc, storage,
#                             CV_HOUGH_GRADIENT,
#                             2,
#                             1, 100, 50
#                             )
#
#    circles = circles.asarrayptr(POINTER(CvVect32f))
#    for c in circles:
#        pass
#        
