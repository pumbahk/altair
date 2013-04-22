import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'nose',
    'webtest',
    'pyramid == 1.3.4',
    'pyramid_debugtoolbar',
    'pyramid_fanstatic',
    'pyramid_tm',
    'pyramid_mailer',
    'pyramid_beaker',
    'pyramid_layout',
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
    'js.bootstrap-ts',
    'js.jquery_timepicker_addon',
    'js.jquery_colorpicker',
    'js.i18n',
    'js.jquery_cookie',
    'js.jqgrid',
    'simplejson',
    'waitress',
    'altair-commons',
    'lxml',
    'isodate',
    'python-dateutil',
    'standardenum',
    'pyramid_who',
    'repoze.who',
    'beaker >= 1.6.4',
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
    'pystache == 0.5.2',
    'repoze.browserid',
    'redis',
    'beaker-extensions == 0.2.0dev-moriyoshi2',
    'boto',
    'fluent-logger == 0.3.3moriyoshi2',
    'PIL', # for qrcode.image.pil
    'altair.findable_label', 
    'altair.log',
    "jsonrpclib", 
    "poster",
    "radix",
    "altair.auth",
    "altair.exclog",
    "altair.now",
    "altair.logicaldeleting",
    "altair.mq",
    "altair.pyramid_assets",
    "altair.pyramid_boto",
    ]

tests_require = [
    "nose", 
    "coverage"
]

extras_require = {
    "testing": tests_require
}

setup(name='ticketing',
      version='0.0',
      use_date_versioning=True,
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
      setup_requires=["altair.versiontools"],
      dependency_links = [
        'file:../commons#egg=altair-commons-0.0',
        'file:../altair_versiontools#egg=altair.versiontools-1.0',
        "file:../altair_findable_label#egg=altair.findable_label-0.0", 
        "file:../altair_log#egg=altair.log-0.0", 
        "file:../altair_auth#egg=altair.auth-1.0", 
        "file:../altair_exclog#egg=altair.exclog-0.0", 
        "file:../altair_now#egg=altair.now-0.0", 
        "file:../altair_logicaldeleting#egg=altair.logicaldeleting-0.0", 
        "file:../altair_mq#egg=altair.mq-0.0", 
        "file:../altair_pyramid_assets#egg=altair.pyramid_assets-0.0.1",
        "file:../altair_pyramid_boto#egg=altair.pyramid_boto-0.0.1",
        'file:../bundle/js.bootstrap_ts-2.3.2.dev1-py2.7.egg',
        'https://github.com/moriyoshi/tableau/tarball/master#egg=tableau-0.0.4pre2',
        "https://github.com/numpy/numpy/tarball/v1.6.2#egg=numpy-1.6.2",
        'https://github.com/moriyoshi/beaker_extensions/tarball/0.2.0dev-moriyoshi2#egg=beaker-extensions-0.2.0dev-moriyoshi2',
        'https://github.com/moriyoshi/fluent-logger-python/tarball/0.3.3moriyoshi2#egg=fluent-logger-0.3.3moriyoshi2',
        'http://py-radix.googlecode.com/files/py-radix-0.5.tar.gz#egg=radix-0.5',
      ],
      tests_require=tests_require,
      extras_require=extras_require, 
      test_suite="ticketing",
      entry_points = """\
      [paste.app_factory]
      main = ticketing:main
      [console_scripts]
      inquiry_demo=ticketing.cart.commands:inquiry_demo
      cancel_auth_expired_carts=ticketing.cart.commands:cancel_auth_expired_carts
      venue_import=ticketing.commands.venue_import:main
      update_seat_status=ticketing.orders.commands:update_seat_status
      join_cart_and_order=ticketing.cart.commands:join_cart_and_order
      sej_notification=ticketing.sej.scripts.sej_notification:main
      check_multicheckout_orders=ticketing.commands.check_multicheckout_orders:main
      populate_order_no=ticketing.commands.populate_order_no:main
      send_sales_reports=ticketing.events.sales_reports.commands:main
      cancel_auth=ticketing.multicheckout.scripts.cancelauth:main
      sej_nwts_upload=ticketing.sej.scripts.sej_nwts_upload:main
      release_carts=ticketing.cart.scripts.release_carts:main
      rakuten_checkout_sales=ticketing.checkout.commands:rakuten_checkout_sales
      refund_order=ticketing.orders.commands:refund_order
      sej_send_refund_file=ticketing.sej.commands:send_refund_file
      """,
      paster_plugins=['pyramid'],
      )

