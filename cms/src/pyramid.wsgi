from pyramid.paster import get_app
application = get_app('/srv/jenkins/cms-testenv/cms/src/testing.ini', 'main')
