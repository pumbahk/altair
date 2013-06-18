from setuptools import setup, find_packages
import os

version = '0.0.2'

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

setup(name='altair.pyramid_boto',
      version=version,
      description="",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Moriyoshi Koizumi',
      author_email='mozo@mozo.jp',
      url='',
      license='mit',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['altair'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'boto',
          'beaker',
          'altair.pyramid_assets',
          # -*- Extra requirements: -*-
      ],
      tests_require=[
          'mock',
      ],
      test_suite='altair.pyramid_boto',
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
