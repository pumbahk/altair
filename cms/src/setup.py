import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    "PIL",
    "gunicorn",
    "venusian>=1.0a3", 
    'pyramid',
    'pyramid_tm',
    'transaction',
    'SQLAlchemy',
    'SQLAHelper',
    "webtest", 
    'alembic',
    'zope.interface',
    # 'zope.sqlalchemy',
    ## utility
    "bpmappers",
    'isodate',
    ## auth
    'oauth2',
    'pyramid_openid',
    ## form
    "WTForms",
    'deform',
    'pyramid_deform',
    ## fanstatic
    'fa.jquery',
    "fanstatic", 
    "pyramid_fanstatic", 
    "js.jquery", 
    "js.bootstrap", 
    "js.json2", 
    "js.jqueryui", 
    "js.jquery_tools", 
    "js.underscore",
    'js.backbone',
    ]

if sys.version_info[:3] < (2,5,0):
    requires.append('pysqlite')

setup(name='altair-cms',
      version='0.0',
      description='altair-cms',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='altaircms',
      install_requires = requires,
      entry_points = """\
      [paste.app_factory]
      main = altaircms:main

      #[paste.paster_command]
      #pscript = scripts.paster:PScript
      #pmain = scripts.paster:PMain

      [console_scripts]
      pscript = scripts.console_scripts:pscript
      pmain = scripts.console_scripts:pmain

      [pyramid.scaffold]
      cms_widget = scaffolds:WidgetPluginTemplate
      cms_asset_widget = scaffolds:AssetWidgetPluginTemplate
      """,
      paster_plugins=['pyramid'],
      )

