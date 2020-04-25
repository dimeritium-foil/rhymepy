#!/bin/env python

from setuptools import setup

setup(
        name='rhymepy',
        version='0.1',
        description='A simple CLI program that highlights rhymes in a given text',
        author='Farris Essam',
        url='https://github.com/dimeritium-foil/rhymepy',
        install_requires=['colored', 'requests'],
        extras_require={'Native rhymes matching via the pronouncing module.': ['pronouncing']},
        packages=['rhymepy'],
        package_data={'': ['default_rhymepy.ini']},
        include_package_data=True,
        entry_points={ "console_scripts": ['rhymepy = rhymepy.main:main'] }
     )
