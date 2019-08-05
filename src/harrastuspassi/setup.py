#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

readme = open('README.rst').read()

setup(
    name='harrastuspassi',
    version='dev',
    description="""""",
    long_description=readme,
    author='Haltu',
    packages=find_packages(),
    include_package_data=True,
    license="",
    zip_safe=False,
    keywords='harrastuspassi',
    install_requires=[
    ],
)
