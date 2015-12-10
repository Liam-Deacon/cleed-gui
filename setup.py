#!/usr/bin/env python
# encoding: utf-8
import os
import sys

#from setuptools import setup, find_packages
#import fix_setuptools_chmod
try:
    from setuptools import find_packages
except ImportError:
    from distutils.core import find_packages

from distutils.core import Extension, setup

if len(sys.argv) == 1:
    sys.argv.append('install')
    
dist = setup(
        name = 'cleed-gui',
        packages = find_packages(),
        version='0.1.0-dev',
        author='Liam Deacon',
        author_email='liam.m.deacon@gmail.com',
        license='GNU General Public License v3.0',
        url='https://pypi.python.org/pypi/cleed-gui',
        description='CLEED front-end for handling LEED-IV calculations',
        long_description=open(os.path.join('src', 'README.rst')
            ).read() if os.path.isfile('README.rst') else None,
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: X11 Applications :: Qt',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering :: Chemistry',
            'Topic :: Scientific/Engineering :: Physics',
            'Topic :: Scientific/Engineering :: Visualization',
            ],
        keywords='cleed-gui LEED-IV diffraction',
        include_package_data = True,
        package_data = {
            # If any package contains *.txt or *.rst files, include them:
            '': ['*.txt', '*.rst', '*.pyw'],
            },
        scripts=[os.path.join("src", "cleed_iv.pyw"),
                 os.path.join("src", "core", "rfac.py")],
        install_requires = ['PySide' or 'PyQt4',    # gui
                            'IPython',              # scripting 
                            'numpy',                # matrix operations
                            'scipy',                # optimisation algorithms
                            'matplotlib',           # graph plots
                            'cython',               # CLEED wrapper
                            'pymol',                # molecular visualiser
                            'phaseshifts'           # phase shift calculations
                            ],
        ext_modules=[],
        window=[os.path.join("src", "cleed-gui.pyw")],
               
)
