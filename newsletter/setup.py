import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'nose',
    'webtest',
    'pyramid',
    'pyramid_debugtoolbar',
    'pyramid_fanstatic',
    'pyramid_tm',
    'pyramid_mailer',
    'pymysql',
    'pymysql_sa',
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
    'WebHelpers',
    'fixture',
    'js.jquery',
    'js.underscore',
    'js.jquery_tools',
    'js.json2',
    'js.jqueryui',
    'js.tinymce',
    'js.backbone',
    'js.bootstrap',
    'simplejson',
    'gunicorn',
    'altair.findable_label', 
    'altair.log',
    'fluent-logger == 0.3.3.post1',
    'altair.exclog', 
    'altair.browserid', 
    'altair.formhelpers',
    'altair.httpsession',
    'altair.multilock',
    ]

setup(name='altair_newsletter',
    version='0.0',
    description='newsletter',
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
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    test_suite='newsletter',
    entry_points = """\
    [paste.app_factory]
    main = newsletter:main
    [console_scripts]
    send_newsletter = newsletter.scripts.send_newsletter:main
    """,
    paster_plugins=['pyramid'],
    )

