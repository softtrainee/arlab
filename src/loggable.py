#!/usr/bin/python
#===============================================================================
# Copyright 2011 Jake Ross
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


# -*- coding: utf-8 -*-

#============= enthought library imports =======================
from traits.api import HasTraits, Any, String, on_trait_change
from pyface.timer.api import do_later
from pyface.message_dialog import warning
from pyface.wx.dialog import confirmation
#============= standard library imports ========================
#============= local library imports  ==========================
from src.helpers.logger_setup import add_console
from globals import show_warnings


class Loggable(HasTraits):

    '''
    '''

    logger = Any(transient=True)
    name = String
    logger_name = String
    # logger_display = None
    def __init__(self, *args, **kw):
        super(Loggable, self).__init__(*args, **kw)
        self._add_logger()

    @on_trait_change('name, logger_name')
    def _add_logger(self):
        '''

        '''
        if self.logger_name:
            name = self.logger_name
        elif self.name:
            name = self.name
        else:
            name = self.__class__.__name__

        #self.logger = add_console(name=name, display=gLoggerDisplay)
        #disable the gLoggerDisplay
        self.logger = add_console(name=name)

    def warning_dialog(self, msg):
        warning(None, msg)

    def confirmation_dialog(self, msg, title=None):
        result = confirmation(None, msg, title=title)
        #NO==5104, YES==5103
        return result == 5103

    def warning(self, msg, decorate=True):
        '''
        '''
        from src.helpers.gdisplays import gWarningDisplay

        if self.logger is not None:
            opened = gWarningDisplay.opened
            if not opened and show_warnings:
                do_later(gWarningDisplay.edit_traits)

            gWarningDisplay.add_text('{} -- {}'.format(self.logger.name.strip(),
                    msg))

            if decorate:
                msg = '****** {}'.format(msg)
            self._log_('warning', msg)
#            self.logger.warning(msg)

    def info(self, msg, decorate=True, dolater=False):
        '''

        '''

#        if self.logger is not None:
        if decorate:
            msg = '====== {}'.format(msg)

        self._log_('info', msg)
#            t = threading.currentThread()
#            if t.name is not 'MainThread':
#                print t.name
#                do_later(self.logger.info, msg)
#            else:
#                self.logger.info(msg)

    def debug(self, msg, decorate=True):
        '''
        '''

#        if self.logger is not None:
#            if decorate:
#                msg = '++++++ {}'.format(msg)
#            self.logger.debug(msg)
        if decorate:
            msg = '++++++ {}'.format(msg)

        self._log_('debug', msg)

    def _log_(self, func, msg):
        if self.logger is None:
            return

        func = getattr(self.logger, func)
        func(msg)

#        t = threading.currentThread()
#        if t.name is not 'MainThread':
#            do_later(func, msg)
#        else:
#            func(msg)
#============= EOF =============================================
