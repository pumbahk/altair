# -*- coding: utf-8 -*-
import optparse
from .. import utils


def start():
    altair_path = utils.AltairPath()
    cmd = altair_path.bin_('supervisord')
    return utils.Shell.system(cmd, sudo=True)


def stop():
    utils.Shell.system('alshain ctl stop all')
    return utils.Shell.system('alshain ctl shutdown')


def reload_():
    utils.Shell.system('alshain ctl reread')
    return utils.Shell.system('alshain ctl update')


def restart():
    utils.Shell.system('alshain daemon stop')
    return utils.Shell.system('alshain daemon start')

CMD_FUNC = {'start': start,
            'stop': stop,
            'reload': reload_,
            'restart': restart,
            }


def main(argv):
    parser = optparse.OptionParser()
    opts, args = parser.parse_args(argv)

    for cmd in args:
        func = CMD_FUNC[cmd]
        func()
