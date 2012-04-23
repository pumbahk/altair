import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_tm',
    'pyramid_openid',
    "pyramid_fanstatic", 
    'sqlahelper',
    "pil",
    "bpmappers",
    'isodate',
    'oauth2',
    "solrpy", 
    "WTForms",
    "js.jquery", 
    "js.bootstrap", 
    "js.json2", 
    "js.jqueryui", 
    "js.jquery_tools", 
    "js.underscore",
    'js.backbone',
    'js.tinymce',
    ]

solr_require = [
    "collective.recipe.solrinstance", 
]

tests_require = [
    "nose",
    "coverage",
    "webtest",
    "mock",
]

devtools_require = [
    "sadisplay",
    "alembic",
    "sphinx",
]

extras_require = {
    "mysql": ["pymysql"],
    "testing": tests_require,
    "gunicorn": ["gunicorn", "gunicorn-console"],
    "devtools": devtools_require,
    "solr": solr_require
}

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
      tests_require=tests_require,
      extras_require=extras_require,
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

      [distutils.commands]
      migrate_db = altaircms.distext.migrate:MigrateCommand
      """,
      paster_plugins=['pyramid'],
      )

