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
import os
import sys
import logging
#=============local library imports  =========================
from paths import root
from filetools import unique_path
from globals import use_debug_logger
from pyface.timer.do_later import do_later
import shutil

FORMAT = '%(name)-12s: %(asctime)s %(levelname)-7s (%(threadName)-10s) %(message)s'
FORMATTER = logging.Formatter(FORMAT)

LEVEL = logging.DEBUG

LOGGER_LIST = []

class DisplayHandler(logging.StreamHandler):
    '''
    '''
    output = None
    def emit(self, record):
        '''

        '''
        if self.output is not None:
            msg = '{record.name}{record.message}'.format(record=record)
#            import wx
#            print type(self.output._display), not isinstance(self.output._display, wx._core._wxPyDeadObject)
#            if not isinstance(self.output._display, wx._core._wxPyDeadObject):

            do_later(self.output.add_text, color='red' if record.levelno > 20 else 'black',
                                 msg=msg,
                                 kind='warning' if record.levelno > 20 else 'info',)
#            self.output.add_text(
#                                     color='red' if record.levelno > 20 else 'black',
#                                 msg=msg,
#                                 kind='warning' if record.levelno > 20 else 'info',
#                                 )
#def clean_logdir(p, cnt):
#    def get_basename(p):
#        p = os.path.basename(p)
#        basename, _tail = os.path.splitext(p)
#        
#        while basename[-1] in '0123456789':
#            basename = basename[:-1]
#        
#        
#        return basename
#    
#    d = os.path.dirname(p)
#    p = os.path.basename(p)
#    b = get_basename(p)
#    print 'cleaning {} for {}'.format(d, b)
#    
#    
#    
#    import tarfile, time
#    name = 'logarchive-{}'.format(time.strftime('%m-%d-%y', time.localtime()))
#    cp, _cnt = unique_path(d, name, filetype='tar')
#    
#    with tarfile.open(cp, 'w') as tar:
#        for i, pi in enumerate(os.listdir(d)):
#            if get_basename(pi) == b and i < (cnt - 5):
#                #print 'compress', i, cnt, pi
#                os.chdir(d)
#                tar.add(pi)
#                os.remove(pi)
#                
#    print 'clean up finished'


def setup(name, level=None):
    '''
    '''

    #make sure we have a log directory
    bdir = os.path.join(root, 'logs')
    if not os.path.isdir(bdir):
        os.mkdir(bdir)

    logpath=os.path.join(bdir, '{}_current.log'.format(name))
    if os.path.isfile(logpath):
        backup_logpath, _cnt = unique_path(bdir, name, filetype='log')
        shutil.copyfile(logpath, backup_logpath)
        os.remove(logpath)
    
    if sys.version.split(' ')[0] < '2.4.0':
        logging.basicConfig()
    else:

        if level is not None:
            level = getattr(logging, level)
        else:
            level = LEVEL

        logging.basicConfig(level=level,
                        format=FORMAT,
                        filename=logpath,
                        filemode='w'
                      )

    if use_debug_logger:

        #main_logger = logging.getLogger()
        #main_logger.setLevel(logging.NOTSET)
        add_console(name='main', level=logging.NOTSET)

def add_console(logger=None, name=None, display=None, level=LEVEL):
    '''

    '''

    if name:
        logger = new_logger(name)

    if logger and logger not in LOGGER_LIST:
        LOGGER_LIST.append(logger)
        #print use_debug_logger, name

        if name == 'main' or not use_debug_logger:
            console = logging.StreamHandler()

            console.setLevel(level)

            # tell the handler to use this format 
            console.setFormatter(FORMATTER)

            logger.addHandler(console)

            #rich text or styled text handlers
            if display:

#                _class_ = 'DisplayHandler'
#                gdict = globals()
#                if _class_ in gdict:
#                    h = gdict[_class_]()
                h = DisplayHandler()
                h.output = display
                h.setLevel(LEVEL)
                h.setFormatter(FORMATTER)
                logger.addHandler(h)

    return logger

def new_logger(name):
    '''
    '''
    if name == 'main':
        l = logging.getLogger()
    else:
        l = logging.getLogger(name)
    return l
