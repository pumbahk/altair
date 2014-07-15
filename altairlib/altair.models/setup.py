from setuptools import setup, find_packages, Extension
import os

version = '0.0'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

requires = [
    "setuptools>0.7",
    "sqlahelper",
    "sqlalchemy",
]

setup(name='altair.models',
      version=version,
      description="",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['altair'],
      include_package_data=True,
      zip_safe=False,
      ext_modules = [
        Extension('altair.models._json_scanner',
                  ['src/altair/models/_json_scanner.c']),
        ],
      install_requires=requires,
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
