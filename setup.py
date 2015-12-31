#!/usr/bin/env python
import os
try:
    import setuptools
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
from setuptools import setup, Extension
from setuptools import find_packages

#mod_cre2 = Extension('_cre2', sources=['_cre2.cpp'], libraries=['re2'],
#                     include_dirs=['/usr/local/include'], extra_compile_args=["-g"],
#                     extra_link_args=["-g"])
#

setup(
    name='cffi_re2',
    version='0.5.0',
    license='MIT license',
    packages=find_packages(exclude=['tests*']),
    install_requires=['cffi>=1.0.2', 'six'],
    #ext_modules=[mod_cre2],
    zip_safe=False,
    test_suite='nose.collector',
    setup_requires=["cffi>=1.0.2"],
    tests_require=['nose'],
    long_description=open("README.md").read(),
    cffi_modules=["cffi_re2/cffi_re2_build.py:ffi"],
    description='Access re2 library using cffi',
    url="https://github.com/vls/cffi_re2"
)
