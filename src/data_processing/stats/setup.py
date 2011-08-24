'''
python setup.py build_ext --inplace

'''

import numpy

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

pychron_dir = '/Users/Ross/Programming/pychron_beta/src'
ext_modules = [Extension("Fflux_gradient_monte_carlo", ["Fflux_gradient_monte_carlo.pyx"],
                         include_dirs = [numpy.get_include(),
                                         pychron_dir
                                         ]
                         )]

setup(
  name = 'Fast Flux Gradient Calculation',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
