#!/usr/bin/env python
# This file is closely based on tests.py from matplotlib
#
# This allows running the matplotlib tests from the command line: e.g.
#
#   $ python tests.py -v -d
#
# The arguments are identical to the arguments accepted by nosetests.
#
# See https://nose.readthedocs.org/ for a detailed description of
# these options.


import nose
# from skxray.testing.noseclasses import KnownFailure
# 
# plugins = [KnownFailure]
plugins = []
env = {"NOSE_WITH_COVERAGE": 1,
       'NOSE_COVER_PACKAGE': 'xray_vision',
       'NOSE_COVER_HTML': 1}
# Nose doesn't automatically instantiate all of the plugins in the
# child processes, so we have to provide the multiprocess plugin with
# a list.
from nose.plugins import multiprocess
multiprocess._instantiate_plugins = plugins


def run():

    nose.main(addplugins=[x() for x in plugins], env=env)


if __name__ == '__main__':
    run()
