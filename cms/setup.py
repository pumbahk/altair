import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid == 1.3',
    'webhelpers', 
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
    "js.bootstrap==2.1.1", 
    "js.json2", 
    "js.jqueryui", 
    "js.jquery_tools", 
    "js.underscore",
    'js.backbone',
    'js.tinymce',
    'pyramid_who',
    'altair-commons',
    'uamobile', 
    'tableau'
    ]

solr_require = [
    "collective.recipe.solrinstance", 
]

tests_require = [
    "nose",
    "coverage",
    "webtest",
    "nosexcover",
    "mock",
]

devtools_require = [
    "sadisplay",
    "alembic",
    "sphinx",
    "sphinxcontrib-blockdiag",
    "sphinxcontrib-seqdiag",
]

extras_require = {
    "mysql": ["pymysql"],
    "testing": tests_require,
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
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      test_suite='altaircms',
      install_requires = requires,
      dependency_links = ['file:../commons#egg=altair-commons-0.0'], 
      tests_require=tests_require,
      extras_require=extras_require,
      entry_points = """\
      [paste.app_factory]
      main = altaircms:main

      [pyramid.scaffold]
      cms_widget = scaffolds:WidgetPluginTemplate
      cms_asset_widget = scaffolds:AssetWidgetPluginTemplate

      [distutils.commands]
      migrate_db = altaircms.distext.migrate:MigrateCommand

      [console_scripts]
      loadfromcsv = altaircms.scripts.loadfromcsv:main
      syncsolr = altaircms.scripts.syncsolr:main
      rendering_page = altaircms.scripts.page_rendering_check:main
      """,
      paster_plugins=['pyramid'],
      )

