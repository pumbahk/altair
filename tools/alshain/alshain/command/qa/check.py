#! /usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import sys
import jumon
import alshain.utils
PATTERN = '^altair.ticketing.*.ini$'


def main(argv=sys.argv[1:]):
    parser = jumon.TransparentArgumentParser()
    parser.add_argument('--verbose', default=False, action='store_true')
    opts = parser.parse_args(argv)
    args = parser.get_unrecognizes()

    alshain_path = alshain.utils.AlshainPath()
    altair_path = alshain.utils.AltairPath()

    regx = re.compile(PATTERN)
    conf_dir = altair_path.conf()
    confs = [altair_path.conf(filename) for filename in os.listdir(conf_dir) if regx.match(filename)]
    script = alshain_path.scripts('show_sej_gateway.py')

    verbose = ''
    if not opts.verbose:
        verbose = '2> /dev/null'
    for conf in confs:

        cmd = 'alshain py {} {} {} {}'.format(script, conf, ' '.join(args), verbose)
        alshain.utils.Shell.system(cmd)

if __name__ == '__main__':
    main()
