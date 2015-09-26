from __future__ import (absolute_import, division, print_function)

try:
    from setuptools import setup
except ImportError:
    try:
        from setuptools.core import setup
    except ImportError:
        from distutils.core import setup

import setuptools
import versioneer


setup(
    name='xray-vision',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Brookhaven National Lab',
    packages=setuptools.find_packages(),
)
