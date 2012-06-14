import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'nose',
    'webtest',
    'pyramid >= 1.3',
    'pyramid_debugtoolbar',
    'pyramid_fanstatic',
    'pyramid_tm',
    'pyramid_mailer',
    'pyramid_beaker',
    'pymysql',
    'mako',
    'stucco_evolution',
    'deform',
    'wtforms',
    'wtforms-recaptcha',
    'sqlalchemy',
    'zope.sqlalchemy',
    'transaction',
    'pastescript',
    'sadisplay',
    'sqlahelper',
    'py4j',
    'WebHelpers',
    'fixture',
    'js.jquery',
    'js.jquery_validation_engine',
    'js.underscore',
    'js.jquery_tools',
    'js.json2',
    'js.jqueryui',
    'js.tinymce',
    'js.backbone',
    'js.bootstrap==2.1.1',
    'js.jquery_timepicker_addon',
    'js.jquery_colorpicker',
    'simplejson',
    'waitress',
    'altair-commons',
    'lxml',
    'isodate',
    'python-dateutil',
    'standardenum',
    ]

setup(name='ticketing',
      version='0.0',
      description='ticketing',
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
      keywords='web pyramid pylons',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      dependency_links = ['file:../../js.jquery_colorpicker#egg=js.jquery_colorpicker-0.0.0', 'file:../commons#egg=altair-commons-0.0'],
      tests_require=requires,
      test_suite="ticketing",
      entry_points = """\
      [paste.app_factory]
      main = ticketing:main
      """,
      paster_plugins=['pyramid'],
      )

