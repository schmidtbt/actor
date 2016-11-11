# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='actor',
    version='0.0.1',
    description='Simple actor model in python',
    long_description=readme,
    author='Benjamin Schmidt',
    author_email='bschmidt@cortexsis.com',
    url='https://github.com/schmidtbt/actor',
    license=license,
    packages=find_packages(exclude=('tests',))
)
