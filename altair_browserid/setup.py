from setuptools import setup, find_packages
import os

version = '1.0'

requires = [
    "webob",
    "altair.request",
    ]

tests_require = [
    "webtest",
    "nose",
    "coverage",
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

setup(name='altair.browserid',
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
      test_suite="altair.browserid",
      install_requires=requires,
      tests_require=tests_require,
      extras_require={
        "testing": tests_require,
        },
      entry_points={
        "paste.filter_factory": [
            "browserid=altair.browserid:browserid_filter_factory",
            ],
        },
      )
