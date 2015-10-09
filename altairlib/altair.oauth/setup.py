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

setup(name='altair.oauth',
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
      url='https://github.com/ticketstar/altair',
      license='proprietary',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['altair'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          ],
      extras_require={
        'openid': ['pyjwt']
        },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
