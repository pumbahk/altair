from setuptools import setup, find_packages
import os

version = '0.0.0'

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
    'setuptools',
    'pyramid',
    'sqlalchemy',
    'sqlahelper',
    'marshmallow==3.0.0b7'
]

setup(name='altair.restful_framework',
      version=version,
      description="",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Nan-Tsou Liu',
      author_email='nantsou.liu@rakuten.com',
      url='http://github.com/ticketstar/altair',
      license='proprietary',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['altair'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      test_suite='altair.restful_framework',
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
