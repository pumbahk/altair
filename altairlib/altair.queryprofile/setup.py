from setuptools import setup, find_packages
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
    "pyramid",
    "sqlalchemy",
    "fanstatic",
    "js.bootstrap",
    "pyramid_dogpile_cache",
]

tests_require = [
    "testfixtures",
]

setup(name='altair.queryprofile',
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
      install_requires=requires,
      tests_require=tests_require,
      extras_require={
          "testing": tests_require,
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
