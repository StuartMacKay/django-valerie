#!/usr/bin/env python

# The entire package configuration is defined in setup.cfg. This ability
# was added in setuptools 30.3.0 (8 Dec 2016). In addition this file is
# not really needed. As of setuptools 40.9.0. if setup.py is not present
# then a default one is emulated where a single call to setup() is made.
# We're keeping setup.py for now since setup.cfg is a bit of a jumble
# with packaging and configs for development all mixed together. It's
# nice to have everything in one place but it's not easy to follow.

from setuptools import setup

setup()
