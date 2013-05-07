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
#============= local library imports  ==========================

try:
    from cv2 import VideoCapture, VideoWriter, imwrite, line
    from cv import ConvertImage, fromarray, LoadImage, Flip, \
        Resize, CreateImage, CvtColor, Scalar, CreateMat

    from cv import CV_CVTIMG_SWAP_RB, CV_8UC1, CV_BGR2GRAY, CV_GRAY2BGR, \
        CV_8UC3, CV_RGB
except ImportError:
    print 'OpenCV required'

def get_focus_measure(src, kind):
    return -1

def crop(src):
    return src

def save_image(src, path):
    imwrite(path, src)

def colorspace(src, cs=None):
    '''

    '''
    if cs is None:
        cs = CV_GRAY2BGR

    if src.channels() == 1:
        dst = CreateImage(src.cols, src.rows, CV_8UC3)
#        dst = cv.Mat(cv.Size(src.cols, src.rows), cv.CV_8UC3)
#        dst = new_dst(src, nchannels=3)
        CvtColor(src, dst, cs)
    else:
        dst = src
    return dst

def grayspace(src):
    if src.channels() > 1:
        dst = CreateImage(src.width, src.height, CV_8UC1)
#        dst = cv.Mat(src.size(), cv.CV_8UC1)  # cv.Size(src.cols, src.rows), cv.CV_8UC1)
        CvtColor(src, dst, CV_BGR2GRAY)
    else:
        dst = src

def resize(src, w, h, dst=None):
    if isinstance(dst, tuple):
        dst = CreateMat(*dst)

    if dst is None:
        dst = CreateMat(int(h), int(w), CV_8UC3)

    Resize(src, dst)
    return dst

def flip(src, mode):
    Flip(src, src, mode)
    return src

def get_size(src):
    return src.size()

def swap_rb(src):
    try:
        ConvertImage(src, src, CV_CVTIMG_SWAP_RB)
    except TypeError:
        src = fromarray(src)
        ConvertImage(src, src, CV_CVTIMG_SWAP_RB)
    return src

def asMat(arr):
    return fromarray(arr)

def load_image(p):
    return LoadImage(p)

def get_capture_device():
    v = VideoCapture()
    return v

def new_video_writer(path, fps, size):
    fourcc = 'MJPG'
    v = VideoWriter(path, fourcc, fps, size)
    return v


#===============================================================================
# drawing
#===============================================================================
def new_point(x, y):
    return x, y
#    return Point(x,y)
def convert_color(color):
    if isinstance(color, tuple):
#        color = (color[2], color[1], color[0])
#        color = (color[0], color[1], color[2])
        color = CV_RGB(*color)
    else:
        color = Scalar(color)
    return color

def draw_lines(src, lines, color=(255, 0, 0), thickness=3):
    if lines:
        for p1, p2 in lines:
            p1 = new_point(*p1)
            p2 = new_point(*p2)
            line(src, p1, p2,
                   convert_color(color), thickness, 8)
#============= EOF =============================================
