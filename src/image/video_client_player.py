import wx
from threading import Thread, Lock
from numpy import fromstring
import time
from Queue import Queue
# Demonstrates how to use wxPython and OpenCV to create a video player
#
# Written by lassytouton
#
# Works with OpenCV 2.3.1
#
# Borrows from "Playing a movie" (http://opencv.willowgarage.com/wiki/wxpython)
#
# Icons film.png, control_stop.png, and control_play.png were sourced from
# Mark James' Silk icon set 1.3 at http://www.famfamfam.com/lab/icons/silk/

WIDTH = 1280
HEIGHT = 720
class Client(Thread):
    data = None
    queue = None
    def run(self):
#        print 'lisenting'
#        plot = self.imgplot
#
#        fp = 1 / 10.0
#        check = True
        import zmq
        self._lock = Lock()
        self.queue = Queue()
        context = zmq.Context()
        self._sock = context.socket(zmq.SUB)
        self._sock.connect('tcp://localhost:5556')
        self._sock.setsockopt(zmq.SUBSCRIBE, '')

#        wxBmap = wx.EmptyBitmap(1, 1)     # Create a bitmap container object. The size values are dummies.
#        filename = '/Users/ross/Sandbox/snapshot001.jpg'
#        wxBmap.LoadFile(filename, wx.BITMAP_TYPE_ANY)
#        self.data = wxBmap
##
        while 1:
            data = self._sock.recv()
            data = fromstring(data, dtype='uint8')
            with self._lock:
                self.data = data
            time.sleep(1e-7)


    def get_frame(self):
        with self._lock:
            return self.data

class VideoClientPlayer(wx.Frame):
    DEFAULT_TOTAL_FRAMES = 300

    DEFAULT_FRAME_WIDTH = 500
    DEFAULT_FRAME_HEIGHT = 300

    ID_OPEN = 1
    ID_SLIDER = 2
    ID_STOP = 3
    ID_PLAY = 4

    ID_TIMER_PLAY = 5

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, title="wxPython OpenCV Video Player - Version 1.0.0",
                          size=(WIDTH, HEIGHT)
                          )

        self.SetDoubleBuffered(True)

        self.client = Client()
        self.client.start()

        self.obmp = wx.EmptyBitmap(WIDTH, HEIGHT)
        self.bmp = wx.EmptyBitmap(WIDTH, HEIGHT)
        self.playing = False

        self.displayPanel = wx.Panel(self, -1)

#        self.displayPanel.SetBackgroundColour('red')
        self.ToolBar = self.CreateToolBar(style=wx.TB_BOTTOM | wx.TB_FLAT)
#        openFile = self.ToolBar.AddLabelTool(self.ID_OPEN, '', wx.Bitmap('film.png'))
#        self.ToolBar.AddSeparator()
#        self.slider = wx.Slider(self.ToolBar, self.ID_SLIDER, 0, 0, self.DEFAULT_TOTAL_FRAMES - 1, None, (self.DEFAULT_FRAME_WIDTH - 100, 50), wx.SL_HORIZONTAL)
#        self.ToolBar.AddControl(self.slider)
        self.ToolBar.AddSeparator()

        stop = self.ToolBar.AddLabelTool(self.ID_STOP, '', wx.Bitmap('control_stop.png'))
        play = self.ToolBar.AddLabelTool(self.ID_PLAY, '', wx.Bitmap('control_play.png'))

#        self.Bind(wx.EVT_TOOL, self.onOpenFile, openFile)
#        self.Bind(wx.EVT_SLIDER, self.onSlider, self.slider)
        self.Bind(wx.EVT_TOOL, self.onStop, stop)
        self.Bind(wx.EVT_TOOL, self.onPlay, play)

        self.playTimer = wx.Timer(self, self.ID_TIMER_PLAY)

        self.Bind(wx.EVT_TIMER, self.onNextFrame, self.playTimer)

        self.Bind(wx.EVT_IDLE, self.onIdle)
        self.Bind(wx.EVT_PAINT, self.onPaint)

        self.ToolBar.Realize()
        self.Show(True)

    def _get_best_size(self):
        (window_width, _) = self.GetSizeTuple()
        new_height = window_width / (WIDTH / float(HEIGHT))
        new_size = (window_width, new_height)
        return new_size

    def _set_bitmap_size(self, bmp):
        if bmp:
            image = wx.ImageFromBitmap(bmp)
            w, h = self._get_best_size()
            image = image.Scale(w, h)
            return wx.BitmapFromImage(image)

    def updateVideo(self):
        frame = self.client.get_frame()

        if frame is not None:
            self.obmp.CopyFromBuffer(frame)
            self.bmp = self._set_bitmap_size(self.obmp)

        self.Refresh()

    def onNextFrame(self, evt):
        self.updateVideo()

    def onStop(self, evt):
        self.playTimer.Stop()
        self.playing = False

    def onPlay(self, evt):
#        fps = cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FPS)
#        if fps != 0:
#            self.playTimer.Start(1000 / fps)#every X ms
#        else:
#        frame = self.capture.get_frame()


#        self.bmp = wx.BitmapFromBuffer(w, h, frame)
#        self.SetSize((w, h))
        self.playTimer.Start(1000 / 15)#assuming 15 fps
        self.playing = True

    def onIdle(self, evt):
        pass
#        if (self.capture):
#            if (self.ToolBar.GetToolEnabled(self.ID_OPEN) != (not self.playing)):
#                self.ToolBar.EnableTool(self.ID_OPEN, not self.playing)
#            if (self.slider.Enabled != (not self.playing)):
#                self.slider.Enabled = not self.playing
#            if (self.ToolBar.GetToolEnabled(self.ID_STOP) != self.playing):
#                self.ToolBar.EnableTool(self.ID_STOP, self.playing)
#            if (self.ToolBar.GetToolEnabled(self.ID_PLAY) != (not self.playing)):
#                self.ToolBar.EnableTool(self.ID_PLAY, not self.playing)
#        else:
#            if (not self.ToolBar.GetToolEnabled(self.ID_OPEN)):
#                self.ToolBar.EnableTool(self.ID_OPEN, True)
#            if (self.slider.Enabled):
#                self.slider.Enabled = False
#            if (self.ToolBar.GetToolEnabled(self.ID_STOP)):
#                self.ToolBar.EnableTool(self.ID_STOP, False)
#            if (self.ToolBar.GetToolEnabled(self.ID_PLAY)):
#                self.ToolBar.EnableTool(self.ID_PLAY, False)

    def onPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0, True)
#        evt.Skip()

if __name__ == "__main__":
    app = wx.App()
    app.RestoreStdio()

    VideoClientPlayer(None)
    app.MainLoop()

    import os
    os._exit(0)
