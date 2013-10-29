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
#============= standard library imports ========================
#============= local library imports  ==========================
from src.displays.gdisplays import gTraceDisplay
from src.envisage.tasks.tasks_plugin import myTasksPlugin
from src.helpers.logger_setup import new_logger
from src.logger.tasks.logger_plugin import LoggerPlugin
from src.initialization_parser import InitializationParser


logger = new_logger('launcher')

PACKAGE_DICT = dict(
    ExperimentPlugin='src.experiment.tasks.experiment_plugin',
    LoadingPlugin='src.loading.loading_plugin',
    ExtractionLinePlugin='src.extraction_line.tasks.extraction_line_plugin',
    VideoPlugin='src.image.tasks.video_plugin',
    #                   CanvasDesignerPlugin='src.canvas.plugins.canvas_designer_plugin',
    #                   MDDModelerPlugin='src.modeling.plugins.mdd_modeler_plugin',

    #                   SVNPlugin='src.svn.plugins.svn_plugin',

    FusionsDiodePlugin='src.lasers.tasks.plugins.diode',
    FusionsCO2Plugin='src.lasers.tasks.plugins.co2',
    FusionsUVPlugin='src.lasers.tasks.plugins.uv',
    CoreLaserPlugin='src.lasers.tasks.plugins.laser_plugin',
    #                   FusionsDiodePlugin='src.lasers.plugins.fusions.diode.plugin',
    #                   FusionsCO2Plugin='src.lasers.plugins.fusions.co2.plugin',
    #                   FusionsUVPlugin='src.lasers.plugins.fusions.uv.plugin',

    #                   SynradCO2Plugin='src.lasers.plugins.synrad_co2_plugin',

    SpectrometerPlugin='src.spectrometer.tasks.spectrometer_plugin',

    #                   GraphPlugin='src.graph.plugins.graph_plugin',

    #                   TwitterPlugin='src.social.plugins.twitter_plugin',

    EmailPlugin='src.social.tasks.email_plugin',
    ProcessingPlugin='src.processing.tasks.processing_plugin',

    MediaServerPlugin='src.media_server.tasks.media_server_plugin',
    PyScriptPlugin='src.pyscripts.tasks.pyscript_plugin',
    DatabasePlugin='src.database.tasks.database_plugin',
    CanvasDesignerPlugin='src.canvas.tasks.canvas_plugin',
    ArArConstantsPlugin='src.constants.tasks.arar_constants_plugin'

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
                       extra={'threadName_': 'Launcher'}
        )
    return klass


def get_plugin(pname):
    klass = None
    if not pname.endswith('Plugin'):
        pname = '{}Plugin'.format(pname)

    #print PACKAGE_DICT.keys()
    #print pname,pname in PACKAGE_DICT.keys()
    if pname in PACKAGE_DICT:
        package = PACKAGE_DICT[pname]
        klass = get_klass(package, pname)

    if klass is not None:
        plugin = klass()
        if isinstance(plugin, Plugin):
            check = plugin.check()
            if check is True:
                return plugin
            else:
                logger.warning('****** {} not available {}******'.format(klass, check),
                               extra={'threadName_': 'Launcher'})
        else:
            logger.warning('***** Invalid {} needs to be a subclass of Plugin ******'.format(klass),
                           extra={'threadName_': 'Launcher'})


def get_user_plugins():
    """
    """
    # append plugins dir to the sys path
    #    sys.path.append(plugins_dir)

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
    """
        assemble the plugins
        return a Pychron TaskApplication
    """
    plugins = [
        CorePlugin(),
        myTasksPlugin(),
        LoggerPlugin()]

    plugins += get_hardware_plugins()
    plugins += get_user_plugins()

    app = klass(plugins=plugins)
    return app


def check_dependencies():
    """
        check the dependencies and
    """
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
    """
    """

    if not check_dependencies():
        return

    app = app_factory(klass)

    try:
        app.run()
        logger.info('Quitting {}'.format(app.name), extra={'threadName_': 'Launcher'})
    except Exception:
        logger.exception('Launching error')
        import traceback

        tb = traceback.format_exc()
        gTraceDisplay.add_text(tb)
        gTraceDisplay.edit_traits(kind='livemodal')

    finally:
        app.exit()

    return


#============= EOF ====================================
