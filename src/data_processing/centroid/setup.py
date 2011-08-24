'''

http://docs.cython.org/src/quickstart/build.html

python setup.py build_ext --inplace
'''

import numpy
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension("centroid", ["centroid.pyx"],

				        include_dirs = [numpy.get_include(),
                         #pychron_dir
                         ]
				)]

setup(
  name = 'centroid',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
