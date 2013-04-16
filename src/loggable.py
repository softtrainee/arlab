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

#============= enthought library imports =======================
from traits.api import HasTraits, Any, String, on_trait_change
from pyface.timer.api import do_later
from pyface.message_dialog import information, warning as nonmodal_warning, \
    MessageDialog
# from pyface.api import confirm
from pyface.wx.dialog import confirmation, warning

#============= standard library imports ========================
# import wx
#============= local library imports  ==========================
# from src.helpers.logger_setup import add_console
from globals import globalv
from src.helpers.color_generators import colorname_generator
from src.helpers.logger_setup import new_logger, NAME_WIDTH

color_name_gen = colorname_generator()

class Loggable(HasTraits):

    '''
    '''
    application = Any
    logger = Any(transient=True)
    name = String
    logger_name = String
    use_logger_display = True
    use_warning_display = True
    logcolor = 'black'
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

        self.logger = new_logger(name)
        c = color_name_gen.next()
        if c in [ 'gray', 'silver', 'greenyellow']:
            c = color_name_gen.next()
        self.logcolor = c

    def warning_dialog(self, msg, sound=None, title=''):
        dialog = MessageDialog(
                               parent=None, message=msg, title=title,
                               severity='warning'
                               )
        if sound:
            from src.helpers.media import loop_sound
            evt = loop_sound(sound)
            dialog.close = lambda: self._close_warning(evt)

        dialog.open()


    def _close_warning(self, evt):
        print evt
        evt.set()
        return True

    def confirmation_dialog(self, msg, title=''):
        result = confirmation(None, msg, title=title)
        # NO==5104, YES==5103
        return result == 5103


    def information_dialog(self, msg, title=None):
        if title is None:
            information(None, msg)
        else:
            information(None, msg, title=title)

    def db_save_dialog(self):
        return self.confirmation_dialog('Save to Database')

    def warning(self, msg, decorate=True):
        '''
        '''

        if self.logger is not None:
            if self.use_warning_display:
                from src.helpers.gdisplays import gWarningDisplay
                if globalv.show_warnings:
                    if not gWarningDisplay.opened and not gWarningDisplay.was_closed:
                        do_later(gWarningDisplay.edit_traits)

                gWarningDisplay.add_text('{{:<{}s}} -- {{}}'.format(NAME_WIDTH).format(self.logger.name.strip(), msg))

            if decorate:
                msg = '****** {}'.format(msg)
            self._log_('warning', msg)

    def info(self, msg, decorate=True, dolater=False):
        '''

        '''
        if self.logger is not None:
            if self.use_logger_display:
                from src.helpers.gdisplays import gLoggerDisplay
                if globalv.show_infos:
                    if not gLoggerDisplay.opened and not gLoggerDisplay.was_closed:
                        do_later(gLoggerDisplay.edit_traits)

                args = ('{{:<{}s}} -- {{}}'.format(NAME_WIDTH).format(self.logger.name.strip(),
                        msg))
                gLoggerDisplay.add_text(args)

            if decorate:
                msg = '====== {}'.format(msg)

            self._log_('info', msg)

    def close_displays(self):
        from src.helpers.gdisplays import gLoggerDisplay, gWarningDisplay
        gLoggerDisplay.close()
        gWarningDisplay.close()

    def debug(self, msg, decorate=True):
        '''
        '''

        if decorate:
            msg = '++++++ {}'.format(msg)

        self._log_('debug', msg)

    def _log_(self, func, msg):
        if self.logger is None:
            return

        func = getattr(self.logger, func)
        func(msg)

#============= EOF =============================================
