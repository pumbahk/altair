from setuptools import setup, find_packages

version = '1.0'

requires = [
    "setuptools>0.7",
    "pika",
    "tornado",
    "pyramid",
    "venusian",
    "six",
]

points = {
    "console_scripts": [
        "mserve=altair.mq.scripts.mserve:main",
    ],
}

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

setup(name='altair.mq',
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
      test_suite='altair.mq',
      entry_points=points,
      )
