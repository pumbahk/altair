import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'nose',
    'webtest',
    'testfixtures',
    'pyramid == 1.5.1',
    'pyramid_mako == 1.0.2',
    'pyramid_debugtoolbar',
    'pyramid_fanstatic',
    'pyramid_tm',
    'pyramid_mailer',
    'pyramid_beaker',
    'pyramid_layout >= 0.9',
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
    'js.i18n',
    'js.jquery_cookie',
    'js.jqgrid-ts',
    'js.bootstrap-datepicker-ts',
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
    'beaker-extensions == 0.2.0.post1',
    'boto',
    'fluent-logger == 0.3.3.post1',
    'Pillow', # for qrcode.image.pil
    'altair.findable_label',
    'altair.log',
    "jsonrpclib",
    "poster",
    "radix",
    "requests",
    "pyOpenSSL",
    "altair.augus",
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
    'altair.keybreak',
    'altair.svg',
    'altair.models',
    'altair.httpsession',
    'altair.samarker',
    'altair.pyramid_dynamic_renderer',
    'altair.timeparse',
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
      tests_require=tests_require,
      extras_require=extras_require,
      test_suite="altair.app.ticketing",
      entry_points = """\
      [paste.app_factory]
      main = altair.app.ticketing:main
      zea-admin = altair.app.ticketing.project_specific.zea:main
      [console_scripts]
      inquiry_demo=altair.app.ticketing.cart.commands:inquiry_demo
      release_carts=altair.app.ticketing.cart.commands:release_carts
      venue_import=altair.app.ticketing.scripts.venue_import:main
      frontend_venue_import=altair.app.ticketing.scripts.frontend_venue_import:main
      update_seat_status=altair.app.ticketing.orders.scripts:update_seat_status
      join_cart_and_order=altair.app.ticketing.cart.commands:join_cart_and_order
      sej_notification=altair.app.ticketing.sej.scripts.sej_notification:main
      check_multicheckout_orders=altair.app.ticketing.scripts.check_multicheckout_orders:main
      populate_order_no=altair.app.ticketing.scripts.populate_order_no:main
      send_sales_reports=altair.app.ticketing.events.sales_reports.commands:main
      send_lots_reports=altair.app.ticketing.events.lots.commands.send_lot_report_mails:main
      cancel_auth=altair.app.ticketing.multicheckout.scripts.cancelauth:main
      sej_nwts_upload=altair.app.ticketing.sej.scripts.sej_nwts_upload:main
      rakuten_checkout_sales=altair.app.ticketing.checkout.commands:rakuten_checkout_sales
      refund_order=altair.app.ticketing.orders.scripts:refund_order
      import_point_grant_results=altair.app.ticketing.loyalty.commands:import_point_grant_results
      import_point_grant_data=altair.app.ticketing.loyalty.commands:import_point_grant_data
      export_point_grant_data=altair.app.ticketing.loyalty.commands:export_point_grant_data
      make_point_grant_data=altair.app.ticketing.loyalty.commands:make_point_grant_data
      detect_fraud=altair.app.ticketing.orders.scripts:detect_fraud
      import_orders=altair.app.ticketing.orders.scripts:import_orders
      sej_file_download=altair.app.ticketing.sej.scripts.sej_file_download:main
      sej_parse_file=altair.app.ticketing.sej.scripts.sej_parse_file:main
      publish_lot_electing=altair.app.ticketing.events.lots.commands.publish_lot_electing:main
      fix_seat_adjacency=altair.app.ticketing.scripts.fix_seat_adjacency:main
      augus_download=altair.app.ticketing.cooperation.augus.scripts.augus_download:main
      augus_upload=altair.app.ticketing.cooperation.augus.scripts.augus_upload:main
      augus_performance=altair.app.ticketing.cooperation.augus.scripts.augus_performance:main
      augus_ticket=altair.app.ticketing.cooperation.augus.scripts.augus_ticket:main
      augus_distribution=altair.app.ticketing.cooperation.augus.scripts.augus_distribution:main
      augus_putback=altair.app.ticketing.cooperation.augus.scripts.augus_putback:main
      augus_achievement=altair.app.ticketing.cooperation.augus.scripts.augus_achievement:main
      augus_venue_sync_request=altair.app.ticketing.cooperation.augus.scripts.augus_venue_sync_request:main
      augus_venue_sync_response=altair.app.ticketing.cooperation.augus.scripts.augus_venue_sync_response:main
      send_sej_remind_mail=altair.app.ticketing.mails.scripts.send_sej_remind_mail:main
      sej_send_refund_file=altair.app.ticketing.sej.scripts.sej_send_refund_file:main
      sej_update_refund_status=altair.app.ticketing.sej.scripts.sej_update_refund_status:main
      famiport_send_sales_file=altair.app.ticketing.famiport.scripts.famiport_send_sales_file:main
      famiport_send_refund_file=altair.app.ticketing.famiport.scripts.famiport_send_refund_file:main
      download_orders=altair.app.ticketing.scripts.download_orders:main
      send_mail=altair.app.ticketing.scripts.send_mail:main
      """,
      dependency_links = [
        'file:../altairlib/altair.versiontools#egg=altair.versiontools-1.0',
        ],
      paster_plugins=['pyramid'],
      )
