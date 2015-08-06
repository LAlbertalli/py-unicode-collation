#!/usr/bin/python
#

#Setup Package

from setuptools import setup, find_packages
import sys

if sys.version[0] == '2':
    package_dir = {'': 'unicode_col'}
    tests = 'tests'
else:
    package_dir = {'': 'unicode_col3'}
    tests = 'tests3'

setup(
    name = "unicode_col",
    version = "0.1",
    package_dir = package_dir,
    description = 'Python Unicode Collation utilities',
    author = 'Luca Albertalli',
    author_email = 'l.albertalli@gmail.com',
    url = 'https://github.com/LAlbertalli/py-unicode-collation',
    install_requires = ['pyicu>=1.4'],
    test_suite = tests,
)