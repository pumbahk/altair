from setuptools import setup, find_packages
import os

version = '0.0'

requires = [
    "setuptools>0.7",
    "sqlalchemy",
]

tests_require = [
    "nose",
]

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

setup(name='altair.saannotation',
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
      url='',
      license='',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['altair'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires+tests_require,
      extras_require={
          "testing": requires+tests_require,
      },
      test_suite='altair.saannotation',
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
