'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
'''
#=============enthought library imports=======================

#=============standard library imports ========================
import wx
#=============local library imports  ==========================
class PopupWindow(wx.MiniFrame):
    text = None
    def __init__(self, parent, style = None):
        super(PopupWindow, self).__init__(parent, style = wx.NO_BORDER | wx.FRAME_FLOAT_ON_PARENT
                              | wx.FRAME_NO_TASKBAR)
        #self.Bind(wx.EVT_KEY_DOWN , self.OnKeyDown)
#        self.Bind(wx.EVT_CHAR, self.OnChar)
#        self.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
        w = 125
        h = 50

        self.set_size(w, h)
        s = wx.BoxSizer()
        self.SetSizer(s)


        t = wx.StaticText(self, style = wx.TE_MULTILINE | wx.TE_READONLY,
                          size = (w, h)
                          )
        #t = wx.TextCtrl(self, style = wx.TE_READONLY | wx.TE_)
        s.Add(t)
        self.text = t

    def set_size(self, width, height):
        self.SetSize(wx.Size(width, height))

#    def OnChar(self, evt):
#        print("OnChar: keycode=%s" % evt.GetKeyCode())
#        self.GetParent().GetEventHandler().ProcessEvent(evt)

    def Position(self, position, size):
        #print("pos=%s size=%s" % (position, size))
        self.Move((position[0] + size[0], position[1] + size[1]))

    def SetPosition(self, position):
        #print("pos=%s" % (position))
        self.Move((position[0], position[1]))

    def SetText(self, t):
        self.text.SetLabel(t)
#    def ActivateParent(self):
#        """Activate the parent window
#        @postcondition: parent window is raised
#
#        """
#        parent = self.GetParent()
#        parent.Raise()
#        parent.SetFocus()
#
#    def OnFocus(self, evt):
#        """Raise and reset the focus to the parent window whenever
#        we get focus.
#        @param evt: event that called this handler
#
#        """
#        print("On Focus: set focus to %s" % str(self.GetParent()))
#        self.ActivateParent()
#        evt.Skip()
#        
#============= EOF ============================================
