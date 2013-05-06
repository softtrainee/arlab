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
from traits.api import Str
from traitsui.api import View, Group, Item
from envisage.core_plugin import CorePlugin
from envisage.ui.workbench.workbench_plugin import WorkbenchPlugin as ETSWorkbenchPlugin
from envisage.ui.workbench.workbench_preferences_page import WorkbenchPreferencesPage as ETSWorkbenchPreferencesPage
from envisage.api import Plugin
from pyface.timer.do_later import do_later
#============= standard library imports ========================
#============= local library imports  ==========================
from pychron_application import Pychron

from plugins.pychron_workbench_plugin import PychronWorkbenchPlugin
from plugins.pychron_workbench_ui_plugin import PychronWorkbenchUIPlugin

# from src.helpers.paths import plugins_dir


# from src.helpers.logger_setup import add_console
from src.helpers.gdisplays import gLoggerDisplay, gTraceDisplay, gWarningDisplay, \
    gMessageDisplay
from globals import globalv
# import logging
from src.helpers.logger_setup import new_logger

#
# if globalv.open_logger_on_launch:
# #    do_later(gLoggerDisplay.edit_traits)
#    do_later(gLoggerDisplay.show)



logger = new_logger('launcher')
# logger = logging.getLogger('launcher')
# logger = add_console(name='{:<30}'.format('launcher'), display=gLoggerDisplay)

PACKAGE_DICT = dict(
                   DatabasePlugin='src.database.plugins.database_plugin',
                   DatabaseUIPlugin='src.database.plugins.database_ui_plugin',
                   ExperimentPlugin='src.experiment.plugins.experiment_plugin',
                   ExperimentUIPlugin='src.experiment.plugins.experiment_ui_plugin',
#                   ScriptPlugin='src.scripts.plugins.script_plugin',
#                   ScriptUIPlugin='src.scripts.plugins.script_ui_plugin',
                   ExtractionLinePlugin='src.extraction_line.plugins.extraction_line_plugin',
                   ExtractionLineUIPlugin='src.extraction_line.plugins.extraction_line_ui_plugin',
#                   CanvasDesignerPlugin='src.canvas.plugins.canvas_designer_plugin',
#                   CanvasDesignerUIPlugin='src.canvas.plugins.canvas_designer_ui_plugin',
                   MDDModelerPlugin='src.modeling.plugins.mdd_modeler_plugin',
                   MDDModelerUIPlugin='src.modeling.plugins.mdd_modeler_ui_plugin',

#                   SVNPlugin='src.svn.plugins.svn_plugin',
#                   SVNUIPlugin='src.svn.plugins.svn_ui_plugin',

                   FusionsDiodePlugin='src.lasers.plugins.fusions.diode.plugin',
                   FusionsDiodeUIPlugin='src.lasers.plugins.fusions.diode.ui_plugin',
                   FusionsCO2Plugin='src.lasers.plugins.fusions.co2.plugin',
                   FusionsCO2UIPlugin='src.lasers.plugins.fusions.co2.ui_plugin',
                   FusionsUVPlugin='src.lasers.plugins.fusions.uv.plugin',
                   FusionsUVUIPlugin='src.lasers.plugins.fusions.uv.ui_plugin',

                   SynradCO2Plugin='src.lasers.plugins.synrad_co2_plugin',
                   SynradCO2UIPlugin='src.lasers.plugins.synrad_co2_ui_plugin',

                   SpectrometerPlugin='src.spectrometer.plugins.spectrometer_plugin',
                   SpectrometerUIPlugin='src.spectrometer.plugins.spectrometer_ui_plugin',

#                   GraphPlugin='src.graph.plugins.graph_plugin',
#                   GraphUIPlugin='src.graph.plugins.graph_ui_plugin',

                   TwitterPlugin='src.social.plugins.twitter_plugin',
                   TwitterUIPlugin='src.social.plugins.twitter_ui_plugin',
                   EmailPlugin='src.social.plugins.email_plugin',
                   EmailUIPlugin='src.social.plugins.email_ui_plugin',

                   ProcessingPlugin='src.processing.plugins.processing_plugin',
                   ProcessingUIPlugin='src.processing.plugins.processing_ui_plugin',

                   MediaServerPlugin='src.media_server.plugins.media_server_plugin',
                   MediaServerUIPlugin='src.media_server.plugins.media_server_ui_plugin'
                 )

class WorkbenchPreferencesPage(ETSWorkbenchPreferencesPage):
    username = Str

    def traits_view(self):
        user_grp = Group(
                         Item('username'),
                         label='User',
                         show_border=True,
                         )
        v = View(user_grp,
                 Item('prompt_on_exit'),
                 )
        return v

class WorkbenchPlugin(ETSWorkbenchPlugin):
    def _my_preferences_pages_default(self):
        return [WorkbenchPreferencesPage]

    def _create_preferences_manager_service(self, **properties):
        from src.envisage.plugins.pychron_preferences_manager import PychronPreferencesManager
        preferences_manager = PychronPreferencesManager(
            pages=[factory() for factory in self.preferences_pages]
        )

        return preferences_manager

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
    from src.hardware.plugins.hardware_plugin import HardwarePlugin
    from src.hardware.plugins.hardware_ui_plugin import HardwareUIPlugin

    ps = []
    if 'hardware' in ip.get_categories():
        if ip.get_plugins('hardware'):
            ps = [HardwarePlugin(), HardwareUIPlugin()]
    return ps


def get_user_plugins():
    '''
    '''
    def get_klass(package, name):
        try:
            m = __import__(package, gdict, locals(), [name], -1)
            klass = getattr(m, name)

        except ImportError, e:
            import traceback
            traceback.print_exc()
            klass = None
            logger.warning('****** {} could not be imported {} ******'.format(name, e))
        return klass

    # append plugins dir to the sys path
#    sys.path.append(plugins_dir)
    from src.helpers.parsers.initialization_parser import InitializationParser
    plugins = []
    ps = InitializationParser().get_plugins()
    for p in ps:
        pp = []
        gdict = globals()
        pp.append(p + 'Plugin')
        # add UI
        uip = p + 'UIPlugin'
        pp.append(uip)

        for pname in pp:
            klass = None
            if pname in gdict:
                klass = gdict[pname]
            elif pname in PACKAGE_DICT:
                package = PACKAGE_DICT[pname]
                klass = get_klass(package, pname)
            elif not pname.endswith('UIPlugin'):
                # dont warn if uiplugin not available
                logger.warning('***** {} not available ******'.format(pname))

            if klass is not None:
                plugin = klass()
                if isinstance(plugin, Plugin):

                    check = plugin.check()
                    if check is True:
                        plugins.append(plugin)
                    else:
                        logger.warning('****** {} not available {}******'.format(klass, check))
                else:
                    logger.warning('***** Invalid {} needs to be a subclass of Plugin ******'.format(klass))

    return plugins

def app_factory():
    '''
        assemble the plugins 
        return a Pychron WorkbenchApplication
    '''
    plugins = [
               CorePlugin(),
               WorkbenchPlugin(),
               PychronWorkbenchPlugin(),
               PychronWorkbenchUIPlugin(),
               ]

    plugins += get_hardware_plugins()
    plugins += get_user_plugins()

    app = Pychron(plugins=plugins)

    gLoggerDisplay.application = app
    gMessageDisplay.application = app
    gWarningDisplay.application = app
    gTraceDisplay.application = app

    if globalv.open_logger_on_launch:
        do_later(gLoggerDisplay.open_view, gLoggerDisplay)

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



app = None
def launch():
    '''
    '''

    if not check_dependencies():
        return

    global app
    app = app_factory()

    if globalv.test:

        def start_test():
            # run the test suite
            from src.testing.testrunner import run_tests
#            run_tests(logger)

        app.on_trait_change(start_test, 'started')
    def foo():
        for i in range(100):
            app.info('asdfasdffsa {}'.format(i), color='green')
    app.on_trait_change(foo, 'started')


    try:
        app.run()
    except Exception, err:
        logger.exception('Launching error')

        import traceback

        tb = traceback.format_exc()
        gTraceDisplay.add_text(tb)
        gTraceDisplay.edit_traits(kind='livemodal')

#        logger.warning(err)
#        warning(app.workbench.active_window, tb)
        app.exit()

    for gi in [gLoggerDisplay, gTraceDisplay, gWarningDisplay]:
        gi.close_ui()

    logger.info('Quitting Pychron')
    app.exit()


    return


# import unittest
# class tempTest(unittest.TestCase):
#    def testTemp(self):
#        global app
#
#        man = app.get_service('src.extraction_line.extraction_line_manager.ExtractionLineManager')
#        self.assertNotEqual(man, 'ne')
#        self.assertNotEqual(man, None)
#        self.assertEqual(man, None)
#
# def run_tests():
#    def _run():
#        import time
#        time.sleep(3)
#        loader = unittest.TestLoader()
#        suite = loader.loadTestsFromTestCase(tempTest)
#        runner = unittest.TextTestRunner()
#        runner.run(suite)
#
#    from threading import Thread
#    t = Thread(target=_run)
#    t.start()



#============= EOF ====================================
