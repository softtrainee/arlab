
from traits.etsconfig.etsconfig import ETSConfig
from src.paths import paths
from src.helpers.logger_setup import logging_setup
ETSConfig.toolkit = 'qt4'


logging_setup('unittests')

paths.build('_diode')

# from .database import IsotopeTestCase
# from .experiment import ExperimentTest
from .processing import FileSelectorTest