#-*- coding: utf-8 -*-
import os
import optparse
from .. import utils

def main(argv):
    parser = optparse.OptionParser()
    opts, args = parser.parse_args(argv[1:])
    cmdfile = ''
    args = []
    try:
        cmdfile = argv[0]
        args = ' '.join(args)
    except IndexError:
        parser.error('Need command line.')
    cur = utils.DeploySwitcher.get_dir()
    cmd = os.path.join(cur, 'bin', cmdfile)
    conf = os.path.join(cur, 'conf', 'altair.ticketing.batch.ini')
    cmdline = cmd + ' {0} {1}'.format(conf, args)
    return utils.Shell.system(cmdline, sudo=True)
