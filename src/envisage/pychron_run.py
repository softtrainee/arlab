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

from envisage.core_plugin import CorePlugin
from envisage.api import Plugin
from envisage.ui.tasks.tasks_plugin import TasksPlugin
#============= standard library imports ========================
import os
#============= local library imports  ==========================
from src.displays.gdisplays import gTraceDisplay
from src.globals import globalv
from src.helpers.logger_setup import new_logger
from src.logger.tasks.logger_plugin import LoggerPlugin
import sys

logger = new_logger('launcher')

PACKAGE_DICT = dict(
#                   DatabasePlugin='src.database.plugins.database_plugin',
                   ExperimentPlugin='src.experiment.tasks.experiment_plugin',
                   ExtractionLinePlugin='src.extraction_line.tasks.extraction_line_plugin',
                   VideoPlugin='src.image.tasks.video_plugin',
#                   CanvasDesignerPlugin='src.canvas.plugins.canvas_designer_plugin',
#                   MDDModelerPlugin='src.modeling.plugins.mdd_modeler_plugin',

#                   SVNPlugin='src.svn.plugins.svn_plugin',

                   FusionsDiodePlugin='src.lasers.tasks.laser_plugin',
                   FusionsCO2Plugin='src.lasers.tasks.laser_plugin',
                   CoreLaserPlugin='src.lasers.tasks.laser_plugin',
#                   FusionsDiodePlugin='src.lasers.plugins.fusions.diode.plugin',
#                   FusionsCO2Plugin='src.lasers.plugins.fusions.co2.plugin',
#                   FusionsUVPlugin='src.lasers.plugins.fusions.uv.plugin',

#                   SynradCO2Plugin='src.lasers.plugins.synrad_co2_plugin',

                   SpectrometerPlugin='src.spectrometer.tasks.spectrometer_plugin',

#                   GraphPlugin='src.graph.plugins.graph_plugin',

#                   TwitterPlugin='src.social.plugins.twitter_plugin',
#                   EmailPlugin='src.social.plugins.email_plugin',

                   ProcessingPlugin='src.processing.tasks.processing_plugin',

                   MediaServerPlugin='src.media_server.tasks.media_server_plugin',
                   PyScriptPlugin='src.pyscripts.tasks.pyscript_plugin',


                 )

def get_module_name(klass):
    words = []
    wcnt = 0
    for c in klass:
        if c.upper() == c:
            words.append(c.lower())
            wcnt += 1
        else:
            words[wcnt - 1] += c

    return '_'.join(words)

def get_hardware_plugins():
    from src.helpers.parsers.initialization_parser import InitializationParser
    ip = InitializationParser()

    ps = []
    if 'hardware' in ip.get_categories():
        from src.hardware.tasks.hardware_plugin import HardwarePlugin
        if ip.get_plugins('hardware'):
            ps = [HardwarePlugin(), ]
    return ps

def get_klass(package, name):
    try:
        m = __import__(package, globals(), locals(), [name], -1)
        klass = getattr(m, name)

    except ImportError, e:
        import traceback
        traceback.print_exc()
        klass = None
        logger.warning('****** {} could not be imported {} ******'.format(name, e),
                       extra={'threadName_':'Launcher'}
                       )
    return klass

def get_plugin(pname):
    gdict = globals()
    klass = None
    if not pname.endswith('Plugin'):
        pname = '{}Plugin'.format(pname)

    if pname in gdict:
        klass = gdict[pname]
    elif pname in PACKAGE_DICT:
        package = PACKAGE_DICT[pname]
        klass = get_klass(package, pname)
    elif not pname.endswith('UIPlugin'):
        # dont warn if uiplugin not available
        logger.warning('***** {} not available ******'.format(pname),
                       extra={'threadName_':'Launcher'}
                       )

    if klass is not None:
        plugin = klass()
        if isinstance(plugin, Plugin):
            check = plugin.check()
            if check is True:
                return plugin
            else:
                logger.warning('****** {} not available {}******'.format(klass, check),
                               extra={'threadName_':'Launcher'})
        else:
            logger.warning('***** Invalid {} needs to be a subclass of Plugin ******'.format(klass),
                           extra={'threadName_':'Launcher'})


def get_user_plugins():
    '''
    '''
    # append plugins dir to the sys path
#    sys.path.append(plugins_dir)
    from src.helpers.parsers.initialization_parser import InitializationParser
    plugins = []
    ps = InitializationParser().get_plugins()

    core_added = False
    for p in ps:
        # if laser plugin add CoreLaserPlugin
        if p in ('FusionsCO2', 'FusionsDiode'):
            plugin = get_plugin('CoreLaserPlugin')
            if plugin and not core_added:
                core_added = True
                plugins.append(plugin)

        plugin = get_plugin(p)
        if plugin:
            plugins.append(plugin)

    return plugins

def app_factory(klass):
    '''
        assemble the plugins 
        return a Pychron WorkbenchApplication
    '''
    plugins = [
               CorePlugin(),
               TasksPlugin(),
               LoggerPlugin()
               ]

    plugins += get_hardware_plugins()
    plugins += get_user_plugins()

    app = klass(plugins=plugins)
    return app

def check_dependencies():
    '''
        check the dependencies and 
    '''
    from pyface.api import warning
    try:
        mod = __import__('uncertainties',
                         fromlist=['__version__']
                         )
        __version__ = mod.__version__
    except ImportError:
        warning(None, 'Install "{}" package. required version>={} '.format('uncertainties', '2.1'))
        return

    vargs = __version__.split('.')
    maj = vargs[0]
    if int(maj) < 2:
        warning(None, 'Update "{}" package. your version={}. required version>={} '.format('uncertainties',
                                                                                           __version__,
                                                                                           '2.1'
                                                                                           ))
        return

    return True


def launch(klass):
    '''
    '''

    if not check_dependencies():
        return

    app = app_factory(klass)

    try:
        app.run()
        logger.info('Quitting {}'.format(app.name), extra={'threadName_':'Launcher'})
        app.exit()

#         sys.exit()
        # force a clean exit
#         os._exit(0)

    except Exception, err:
        logger.exception('Launching error')

        import traceback

        tb = traceback.format_exc()
        gTraceDisplay.add_text(tb)
        gTraceDisplay.edit_traits(kind='livemodal')

        app.exit()

    return



#============= EOF ====================================
