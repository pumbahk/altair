import csv
import optparse
import os
import sys

from os.path import abspath, dirname
sys.path.append(abspath(dirname(dirname(__file__))))

from pyramid.paster import bootstrap
from ticketing.core.models import ReportSetting, Mailer, session

import logging
logging.basicConfig()

def main(argv=sys.argv):

    config_file = sys.argv[1]
    print config_file
    # configuration
    if config_file is None:
        print 'You must give a config file'
        return

    log_file = os.path.abspath(sys.argv[2])
    print log_file
    logging.config.fileConfig(log_file)
    app_env = bootstrap(config_file)
    registry = app_env['registry']
    settings = registry.settings

if __name__ == '__main__':
    main()

