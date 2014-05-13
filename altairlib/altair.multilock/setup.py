from setuptools import setup, find_packages
import sys, os

version = '0.0'
tests_require = ['nose',
                 'coverage',
                 'mock',
                 ]

setup(name='altair.multilock',
      version=version,
      description="Locking mechanism for altair",
      long_description="Locking mechanism for altair",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='lock',
      author='TakesxiSximada',
      author_email='takesxi.sximada@gmail.com',
      url='',
      license='MIT',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['altair'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'sqlahelper',
          'nose',
          'coverage',
          'mock',
      ],
      # tests_require = tests_require,
      # extras_require={
      #     'testing': tests_require,
      # },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
