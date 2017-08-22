from distutils.core import setup
from Cython.Build import cythonize


setup(
  name = 'CAStar',
  ext_modules = cythonize("CAStar.pyx"),
)
