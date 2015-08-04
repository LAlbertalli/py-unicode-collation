#!/usr/bin/python
#

#Setup Package

from setuptools import setup, find_packages

setup(
    name = "unicode_col",
    version = "0.1",
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    description = 'Python Unicode Collation utilities',
    author = 'Luca Albertalli',
    author_email = 'l.albertalli@gmail.com',
    url = 'https://github.com/LAlbertalli/py-unicode-collation',
    install_requires = ['pyicu>=1.4'],
)