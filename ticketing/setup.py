import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'nose',
    'webtest',
    'pyramid == 1.3',
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
    'js.jquery == 1.7.1',
    'js.jquery_validation_engine',
    'js.underscore >= 1.3.3',
    'js.jquery_tools',
    'js.json2',
    'js.jqueryui',
    'js.jqueryui_bootstrap',
    'js.tinymce',
    'js.backbone',
    'js.bootstrap==2.1.1',
    'js.jquery_timepicker_addon',
    'js.jquery_colorpicker',
    'js.i18n',
    'js.jquery_cookie',
    'simplejson',
    'waitress',
    'altair-commons',
    'lxml',
    'isodate',
    'python-dateutil',
    'standardenum',
    'pyramid_who',
    'repoze.who',
    'beaker',
    'mock',
    'tableau >= 0.0.4pre',
    'uamobile',
    'alembic >= 0.3.3',
    'xlrd',
    'xlwt',
    'xlutils',
    'cssutils',
    'numpy',
    'qrcode',
    'pystache',
    'repoze.browserid',
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
      dependency_links = [
        'file:../commons#egg=altair-commons-0.0',
        'file:../bundle/js.underscore#egg=js.underscore-1.3.3',
        'https://github.com/moriyoshi/tableau/tarball/master#egg=tableau-0.0.4pre',
        'https://bitbucket.org/moriyoshi/alembic/get/9fe8d037f71f.zip#egg=alembic-0.3.5moriyoshi', 
        "https://github.com/numpy/numpy/tarball/v1.6.2#egg=numpy-1.6.2"
      ],
      tests_require=requires,
      test_suite="ticketing",
      entry_points = """\
      [paste.app_factory]
      main = ticketing:main
      [console_scripts]
      inquiry_demo=ticketing.cart.commands:inquiry_demo
      cancel_auth_expired_carts=ticketing.cart.commands:cancel_auth_expired_carts
      """,
      paster_plugins=['pyramid'],
      )

