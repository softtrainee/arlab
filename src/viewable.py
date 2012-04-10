#!/usr/bin/python
# -*- coding: utf-8 -*-

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
from traits.api import Any
from traitsui.api import Handler
from src.loggable import Loggable
from pyface.timer.do_later import do_after


class ViewableHandler(Handler):
    def init(self, info):
        info.object.ui = info.ui
        info.object.opened()

    def close(self, info, is_ok):
        return info.object.close(is_ok)


class Viewable(Loggable):
    ui = Any
    handler_klass = ViewableHandler

    def opened(self):
        pass

    def close(self, ok):
        return ok

    def close_ui(self):
        if self.ui is not None:
            #disposes 50 ms from now
            do_after(1, self.ui.dispose)
            #sleep a little so everything has time to update
            #time.sleep(0.05)

# ============= EOF ====================================
