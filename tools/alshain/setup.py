#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages
#host = '0.0.0.0:4989'
host = 'bitbucket.org'

classifiers = ['Development Status :: 3 - Alpha',
               'Environment :: Console',
               'Environment :: Web Environment',
               'Intended Audience :: Developers',
               'License :: OSI Approved :: BSD License',
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               'Topic :: Documentation',
               'Topic :: Utilities',
               ]
requires = ['jumon',
            'pymysql',
            'enum34',
            'pit',
            'pywad',
            ]

setup(
    name='alshain',
    version='0.2.2',
    url='https://{0}/takesxi_sximada/alshain'.format(host),
    download_url='https://{0}/takesxi_sximada/alshain'.format(host),
    license='MIT',
    author='TakesxiSximada',
    author_email='takesxi.sximada@gmail.com',
    description='Altair Debugging Utility',
    long_description='',
    zip_safe=False,
    classifiers=classifiers,
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    entry_points = """\
    [console_scripts]
    alshain = alshain.command:main
    """
    )
