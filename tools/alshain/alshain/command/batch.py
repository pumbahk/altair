# -*- coding: utf-8 -*-
import os
import jumon
from .. import utils


def main(argv):
    parser = jumon.TransparentOptionParser()
    opts, args = parser.parse_args(argv[1:])
    subcmd_args = ''
    try:
        cmdfile = argv[0]
        subcmd_args = ' '.join(args)
    except IndexError:
        parser.error('Need command line.')
    cur = utils.DeploySwitcher.get_dir()
    cmd = os.path.join(cur, 'bin', cmdfile)
    conf = os.path.join(cur, 'conf', 'altair.ticketing.batch.ini')
    cmdline = cmd + ' {0} {1}'.format(conf, subcmd_args)
    return utils.Shell.system(cmdline, sudo=True)
