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

with open('requirements.txt') as f:
    requirements = f.read().split()

with open('README.md') as f:
    long_description = f.read()

setup(
    name='xray-vision',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Brookhaven National Laboratory',
    description='Visualization widgets and plotting helpers targeted at X-Ray Sciences',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    install_requires=requirements,
    url='https://github.com/Nikea/xray-vision',
)
