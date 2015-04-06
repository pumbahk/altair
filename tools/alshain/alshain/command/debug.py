# -*- coding: utf-8 -*-
import re
import os
import optparse
try:
    import stringio
except ImportError:
    import StringIO as stringio  # noqa

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from . import ctl
from .. import utils


class CommandError(Exception):
    pass


def main(argv):
    parser = optparse.OptionParser()
    parser.parse_args(argv)

    try:
        ctl_name = argv[0]
    except IndexError:
        parser.error('Invalid parameter: {0}'.format(ctl_name))
    else:
        ctl.main(['stop', ctl_name])
        try:
            cmd = utils.get_command(ctl_name)

            regx = re.compile('.*\.ini$', re.I)
            for name in cmd.split():
                if regx.match(name):
                    backup = name + '.alshain'
                    if not os.path.exists(backup):
                        utils.Shell.system('cp {} {}'.format(name, backup), sudo=True)
                    else:
                        raise CommandError(backup)

                    conf = configparser.SafeConfigParser()
                    conf.read(name)
                    conf.set('server:main', 'timeout', '3600')

                    utils.Shell.system('chmod 666 {}'.format(name), sudo=True)
                    with open(name, 'w+b') as fp:
                        conf.write(fp)

                    utils.Shell.system(cmd, sudo=True)

                    utils.Shell.system('rm -f {}'.format(name), sudo=True)
                    utils.Shell.system('mv {} {}'.format(backup, name), sudo=True)
                    break
        finally:
            ctl.main(['start', ctl_name])
