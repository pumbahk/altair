from setuptools import setup, find_packages
version = "0.0.1"

requires = [
    "pyramid"
]

setup(name='altair.log',
      version=version,
      description="",
      keywords='',
      packages=find_packages(),
      namespace_packages=['altair'],
      test_suite="altair.log.tests", 
      install_requires=requires)
