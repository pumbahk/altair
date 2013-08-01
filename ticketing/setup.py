import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'nose',
    'webtest',
    'testfixtures',
    'pyramid == 1.3.4',
    'pyramid_debugtoolbar',
    'pyramid_fanstatic',
    'pyramid_tm',
    'pyramid_mailer',
    'pyramid_beaker',
    'pyramid_layout',
    'pyramid_selectable_renderer >= 0.0.4',
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
    'Pillow', # for qrcode.image.pil
    'altair.findable_label', 
    'altair.log',
    "jsonrpclib", 
    "poster",
    "radix",
    "requests",
    "altair.auth",
    "altair.sqla",
    "altair.exclog",
    "altair.now",
    "altair.logicaldeleting",
    "altair.mq",
    "altair.pyramid_assets",
    "altair.pyramid_boto",
    'altair.pyramid_tz',
    "altair.mobile",
    "altair.grid",
    'altair.saannotation',
    'altair.queryprofile',
    'altair.sqlahelper',
    'altair.viewhelpers',
    'altair.formhelpers',
    ]

tests_require = [
    "nose", 
    "coverage"
    "testfixtures",
]

extras_require = {
    "testing": tests_require
}

setup(name='altair.app.ticketing',
      version='0.0',
      use_date_versioning=True,
      description='altair.app.ticketing',
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
        'file:../altairlib/altair.versiontools#egg=altair.versiontools-1.0',
        "file:../altairlib/altair.findable_label#egg=altair.findable_label-0.0", 
        "file:../altairlib/altair.log#egg=altair.log-0.0.1", 
        "file:../altairlib/altair.auth#egg=altair.auth-1.0", 
        "file:../altairlib/altair.sqla#egg=altair.sqla-1.0", 
        "file:../altairlib/altair.exclog#egg=altair.exclog-0.0", 
        "file:../altairlib/altair.now#egg=altair.now-0.0", 
        "file:../altairlib/altair.logicaldeleting#egg=altair.logicaldeleting-0.0", 
        "file:../altairlib/altair.mq#egg=altair.mq-0.0", 
        "file:../altairlib/altair.pyramid_assets#egg=altair.pyramid_assets-0.0.1",
        "file:../altairlib/altair.pyramid_boto#egg=altair.pyramid_boto-0.0.1",
        "file:../altairlib/altair.mobile#egg=altair.mobile-0.0.1",
        "file:../altairlib/altair.mq#egg=altair.mq-0.0", 
        "file:../altairlib/altair.pyramid_tz#egg=altair.pyramid_tz-0.0.0",
        "file:../altairlib/altair.rakuten_auth#egg=altair.rakuten_auth-0.0.0",
        "file:../altairlib/altair.saannotation#egg=altair.saannotation-0.0",
        'file:../bundle/js.bootstrap_ts-2.3.2.dev2-py2.7.egg',
        'https://github.com/moriyoshi/tableau/tarball/master#egg=tableau-0.0.4pre2',
        "https://github.com/numpy/numpy/tarball/v1.6.2#egg=numpy-1.6.2",
        'https://github.com/moriyoshi/beaker_extensions/tarball/0.2.0dev-moriyoshi2#egg=beaker-extensions-0.2.0dev-moriyoshi2',
        'https://github.com/moriyoshi/fluent-logger-python/tarball/0.3.3moriyoshi2#egg=fluent-logger-0.3.3moriyoshi2',
        'http://py-radix.googlecode.com/files/py-radix-0.5.tar.gz#egg=radix-0.5',
      ],
      tests_require=tests_require,
      extras_require=extras_require, 
      test_suite="altair.app.ticketing",
      entry_points = """\
      [paste.app_factory]
      main = altair.app.ticketing:main
      [console_scripts]
      inquiry_demo=altair.app.ticketing.cart.commands:inquiry_demo
      cancel_auth_expired_carts=altair.app.ticketing.cart.commands:cancel_auth_expired_carts
      venue_import=altair.app.ticketing.scripts.venue_import:main
      update_seat_status=altair.app.ticketing.orders.scripts:update_seat_status
      join_cart_and_order=altair.app.ticketing.cart.commands:join_cart_and_order
      sej_notification=altair.app.ticketing.sej.scripts.sej_notification:main
      check_multicheckout_orders=altair.app.ticketing.scripts.check_multicheckout_orders:main
      populate_order_no=altair.app.ticketing.scripts.populate_order_no:main
      send_sales_reports=altair.app.ticketing.events.sales_reports.commands:main
      send_lots_reports=altair.app.ticketing.events.lots.commands.send_lot_report_mails:main
      cancel_auth=altair.app.ticketing.multicheckout.scripts.cancelauth:main
      sej_nwts_upload=altair.app.ticketing.sej.scripts.sej_nwts_upload:main
      release_carts=altair.app.ticketing.cart.scripts.release_carts:main
      rakuten_checkout_sales=altair.app.ticketing.checkout.commands:rakuten_checkout_sales
      refund_order=altair.app.ticketing.orders.scripts:refund_order
      sej_send_refund_file_with_proxy=altair.app.ticketing.sej.commands:send_refund_file_with_proxy
      import_point_grant_results=altair.app.ticketing.loyalty.commands:import_point_grant_results
      import_point_grant_data=altair.app.ticketing.loyalty.commands:import_point_grant_data
      export_point_grant_data=altair.app.ticketing.loyalty.commands:export_point_grant_data
      make_point_grant_data=altair.app.ticketing.loyalty.commands:make_point_grant_data
      """,
      paster_plugins=['pyramid'],
      )

