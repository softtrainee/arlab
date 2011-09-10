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
'''
@author: Jake Ross
@copyright: 2009
@license: Educational Community License 1.0
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

FORMAT = '%(name)-12s: %(asctime)s %(levelname)s %(message)s'
FORMATTER = logging.Formatter(FORMAT)

LEVEL = logging.INFO

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
            self.output.add_text(
                                 color='red' if record.levelno > 20 else 'black',
                                 msg=msg,
                                 kind='warning' if record.levelno > 20 else 'info',
                                 )

def setup(name, level=None):
    '''
    '''

    #make sure we have a log directory
    bdir = os.path.join(root, 'logs')
    if not os.path.isdir(bdir):
        os.mkdir(bdir)

    logpath = unique_path(bdir, name, filetype='log')

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

def add_console(logger=None, name=None, display=None, level=None):
    '''
            @type name: C{str}
            @param name:
    '''

    if level is  None:
        level = LEVEL

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
                _class_ = 'DisplayHandler'
                gdict = globals()
                if _class_ in gdict:
                    h = gdict[_class_]()
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
