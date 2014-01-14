#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages

ROOT = os.path.dirname(os.path.abspath(__file__))
README_PATH = os.path.join(ROOT, 'README.txt')

try:
    with open(README_PATH, 'rb') as fp:
        long_desc = fp.read()
except:
    long_desc = ''
    
requires = ['enum34',
            'ftputil',
            ]
test_requires = ['nose',
                 'coverage',
                 'pit'
                  ]

setup(
    name='altair.augus',
    version='0.1.0',
    url='https://github.com/ticketstar/altair',
    download_url='https://github.com/ticketstar/altair',
    license='GPL',
    author='TakesxiSximada',
    author_email='takesxi.sximada@gmail.com',
    description='Augus Cooperation',
    long_description=long_desc,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    platforms='any',
    include_package_data=True,
    zip_safe=False,    
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['altair'],
    install_requires=requires,
    test_require=test_requires,
)
