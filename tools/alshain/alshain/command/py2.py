# -*- coding: utf-8 -*-
import jumon
from .. import utils


def main(argv):
    parser = jumon.TransparentArgumentParser()
    parser.add_argument('command')
    parser.add_argument('--conf', default=False, action='store_true')
    parser.add_argument('--option', default=False, action='store_true')
    opts = parser.parse_args(argv)

    argv = parser.get_unrecognizes()
    altair_path = utils.AltairPath()

    if opts.conf:
        conf = altair_path.conf('altair.ticketing.batch.ini')

    args = []

    altairpy = altair_path.bin_('altairpy')
    args.append(altairpy)
    args.append(opts.command)

    if opts.option:
        args.append('-c')
    if opts.conf:
        args.append(conf)
    args += argv

    cmd = jumon.escape_join(args)
    return jumon.Shell.system(cmd)
