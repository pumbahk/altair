import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid == 1.3.4',
    'webhelpers',
    'pyramid_tm',
    "pyramid_fanstatic",
    'sqlahelper',
    "Pillow",
    'isodate',
    "solrpy",
    "WTForms",
    "js.jquery",
    "js.bootstrap",
    "js.json2",
    "js.jqueryui",
    "js.jquery_tools",
    'js.underscore',
    'js.backbone',
    'js.tinymce',
    'js.jquery_form == 3.09',
    'pyramid_who',
    'uamobile',
    'fluent-logger == 0.3.3moriyoshi4',
    'pyramid_selectable_renderer >= 0.0.4',
    'altair.findable_label',
    'altair.log',
    'altair.encodingfixer',
    'altair.exclog',
    'altair.cdnpath',
    'altair.viewhelpers',
    'altair.formhelpers',
    "altair.preview",
    "altair.extracodecs",
    'pyramid_layout',
    'lxml',
    'waitress'
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
    # "sadisplay",
    "alembic",
    # "sphinx",
    # "sphinxcontrib-blockdiag",
    # "sphinxcontrib-seqdiag",
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
      dependency_links = [s.format(**locals()) for s in [
        'file:{here}/../commons#egg=altair-commons-0.0',
        'file:{here}/../altair_findable_label#egg=altair.findable_label-0.0',
        "file:{here}/../altair_log#egg=altair.log-0.0.1", 
        'file:{here}/../altair_encodingfixer#egg=altair.encodingfixer-0.0', 
        'file:{here}/../altair_exclog#egg=altair.exclog-0.0', 
        'file:{here}/../altair_cdnpath#egg=altair.cdnpath-0.0', 
        'https://github.com/moriyoshi/fluent-logger-python/tarball/0.3.3moriyoshi4#egg=fluent-logger-0.3.3moriyoshi4',
        ]],
      tests_require=tests_require,
      extras_require=extras_require,
      entry_points = """\
      [paste.app_factory]
      main = altaircms:main

      [pyramid.scaffold]
      cms_widget = scaffolds:WidgetPluginTemplate
      cms_asset_widget = scaffolds:AssetWidgetPluginTemplate
      functional_tests = scaffolds:FunctionalTestTemplate
      [console_scripts]
      loadfromcsv = altaircms.scripts.loadfromcsv:main
      syncsolr = altaircms.scripts.syncsolr:main
      rendering_page = altaircms.scripts.page_rendering_check:main
      """,
      paster_plugins=['pyramid'],
      )

