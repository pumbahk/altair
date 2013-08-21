from setuptools import setup, find_packages
version = "0.0.0"

requires = [
    "setuptools>0.7",
    "pyramid"
]

setup(name='altair.findable_label',
      version=version,
      description="",
      keywords='',
      packages=find_packages(),
      namespace_packages=['altair'],
      install_requires=requires)
