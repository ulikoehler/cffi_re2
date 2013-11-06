#!/usr/bin/env python
try:
    import setuptools
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
from setuptools import setup, Extension
from setuptools import find_packages


metadata = {}
options = {}
metadata['name'] = 'cffi_re2'
metadata['version'] = '0.1'
metadata['packages'] = find_packages()

mod_cre2 = Extension('_cre2', sources=['_cre2.cpp'], libraries = ['re2'], include_dirs = ['/usr/local/include'])

metadata['install_requires'] = ['cffi==0.7']
metadata['ext_modules'] = [mod_cre2]
metadata['zip_safe'] = False
setup(**metadata)