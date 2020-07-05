#!/bin/env python

from pathlib import Path
from setuptools import setup

# The directory containing this file
HERE = Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
        name='rhymepy',
        version='0.1.0',
        description='A simple CLI program that highlights rhymes in a given text',
        long_description=README,
        long_description_content_type="text/markdown",
        author='Farris Essam',
        url='https://github.com/dimeritium-foil/rhymepy',
        install_requires=['colored', 'requests'],
        extras_require={'Native rhymes matching via the pronouncing module.': ['pronouncing']},
        packages=['rhymepy'],
        package_data={'': ['default_rhymepy.ini']},
        include_package_data=True,
        entry_points={ "console_scripts": ['rhymepy = rhymepy.main:main'] }
     )
