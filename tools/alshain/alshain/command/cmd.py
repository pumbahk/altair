# -*- coding: utf-8 -*-
import os
import sys
import jumon

from .. import utils


def main(argv=sys.argv[1:]):
    parser = jumon.TransparentOptionParser()
    opts, args = parser.parse_args(argv[1:])
    cmdfile = ''
    try:
        cmdfile = argv[0]
        args = ' '.join(args)
    except IndexError:
        parser.error('Need command line.')
    cur = utils.DeploySwitcher.get_dir()
    cmd = os.path.join(cur, 'bin', cmdfile)
    cmdline = cmd + ' {}'.format(args)
    return utils.Shell.system(cmdline, sudo=True)
