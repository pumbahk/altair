#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import jumon
import alshain.utils


def main(argv=sys.argv[1:]):
    parser = jumon.TransparentArgumentParser()
    parser.add_argument('conf', default='altair.ticketing.batch.ini', nargs='?')
    opts = parser.parse_args(argv)
    args = parser.get_unrecognizes()

    alshain_path = alshain.utils.AlshainPath()

    if not os.path.exists(opts.conf):
        altair_path = alshain.utils.AltairPath()
        conf = altair_path.conf(opts.conf)
        if os.path.exists(conf):
            opts.conf = conf
        else:
            parser.error('Not found config: {}'.format(opts.conf))

    retouch_script = alshain_path.scripts('qa_init.py')

    cmd = 'alshain py {} {} {}'.format(retouch_script, opts.conf, ' '.join(args))
    return alshain.utils.Shell.system(cmd)

if __name__ == '__main__':
    main()
