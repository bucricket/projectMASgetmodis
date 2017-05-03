#!/usr/bin/env python

from __future__ import print_function
import os



# set project base directory structure
base = os.getcwd()
    
try:
    from setuptools import setup
    setup_kwargs = {'entry_points': {'console_scripts':['getmodisdata=getmodisdata.getmodisdata:main']}}
except ImportError:
    from distutils.core import setup
    setup_kwargs = {'scripts': ['bin/getmodisdata']}
    
from getmodisdata import __version__




setup(
    name="getmodisdata",
    version=__version__,
    description="get MODIS data",
    author="Mitchell Schull",
    author_email="mitch.schull@noaa.gov",
    url="https://github.com/bucricket/projectMASgetmodis.git",
    packages= ['getmodisdata'],
    platforms='Posix; MacOS X; Windows',
    license='BSD 3-Clause',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        # Uses dictionary comprehensions ==> 2.7 only
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: GIS',
    ],  
    **setup_kwargs
)

