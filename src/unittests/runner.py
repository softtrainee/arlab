
from traits.etsconfig.etsconfig import ETSConfig
from src.paths import paths
from src.helpers.logger_setup import logging_setup
ETSConfig.toolkit = 'qt4'


paths.build('_diode')
logging_setup('unittests')

# from .database import IsotopeTestCase
from .experiment import ExperimentTest
# from .experiment import ExecutorTest
# from .experiment import HumanErrorCheckerTest

# from .processing import FileSelectorTest
# from .york_regression import YorkRegressionTest, NewYorkRegressionTest
# from .regression import NewYorkRegressionTest
# from .bayesian import BayesianTest