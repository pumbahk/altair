# coding: utf-8

import optparse
import sys
from pyramid.paster import bootstrap, setup_logging

def main(argv=sys.argv):
    if len(sys.argv) < 2:
        print "usage: python sej_notification.py development.ini"
        sys.exit()

    ini_file = sys.argv[1]
    env = bootstrap(ini_file)
    setup_logging(ini_file)

    request = env['request']
    registry = env['registry']
    settings = registry.settings

    import transaction
    trans = transaction.begin()
    from ..notification import process_notification
    process_notification(request)
    trans.commit()

if __name__ == u"__main__":
    main(sys.argv)
