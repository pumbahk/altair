#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import (
    setup,
    find_packages,
    )


def find_package_data(target, package_root):
    return [
        os.path.relpath(os.path.join(root, filename), package_root)
        for root, dirs, files in os.walk(target)
        for filename in files
        ]

src = 'src'
install_requires = []
test_require = []
packages = find_packages(src)
package_dir = {'': src}
package_data = {}

requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
with open(requirements_file, 'rb') as fp:
    install_requires.extend(
        map(lambda line: line.strip().decode(),
            fp.readlines()))

setup(
    name='famic',
    version='0.1.0',
    url='-',
    download_url='-',
    license='See http://www.python.org/3.4/license.html',
    author='TakesxiSximada',
    author_email='takesxi.sximada@gmail.com',
    description="famiport client",
    long_description="famiport client",
    zip_safe=False,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.4',
        ],
    platforms='any',
    packages=packages,
    package_dir=package_dir,
    namespace_packages=[
        ],
    package_data=package_data,
    include_package_data=True,
    install_requires=install_requires,
    test_require=test_require,
    entry_points='''
    [console_scripts]
    famic = famic.commands:main
    '''
    )
