#============= enthought library imports =======================
from traits.api import HasTraits, Any, String, on_trait_change
from pyface.timer.api import do_later

#============= standard library imports ========================

#============= local library imports  ==========================
from src.helpers.logger_setup import add_console
from src.helpers.gdisplays import gLoggerDisplay, gWarningDisplay
from globals import show_warnings

MAXLEN = 30
class Loggable(HasTraits):
    '''
    '''
    logger = Any(transient = True)
    name = String
    logger_display = None
    def __init__(self, *args, **kw):
        '''
        '''
        super(Loggable, self).__init__(*args, **kw)
        self._add_logger()

    @on_trait_change('name')
    def _add_logger(self, *args, **kw):
        '''

        '''
        if self.name:
            name = self.name
        else:
            name = self.__class__.__name__
        #self.logger = new_logger(name)


#        name = name + ' ' * (MAXLEN - len(name))
        name = '{:<{}}'.format(name, MAXLEN)
        self.logger = add_console(name = name, display = gLoggerDisplay)

    def warning(self, msg, decorate = True):
        '''
 
        '''
        if self.logger is not None:
            opened = gWarningDisplay.opened
            if not opened and show_warnings:
                do_later(gWarningDisplay.edit_traits)

            gWarningDisplay.add_text('{} -- {}'.format(self.logger.name.strip(), msg))
            if decorate:
                msg = '****** {}'.format(msg)


            self.logger.warning(msg)

    def info(self, msg, decorate = True):
        '''

        '''
        if self.logger is not None:
            if decorate:
                msg = '====== {}'.format(msg)



            self.logger.info(msg)


    def debug(self, msg, decorate = True):
        '''
        '''
        if self.logger is not None:
            if decorate:
                msg = '++++++ {}'.format(msg)
            self.logger.debug(msg)


#============= views ===================================
#============= EOF ====================================
