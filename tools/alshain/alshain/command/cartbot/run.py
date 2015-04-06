# -*- coding: utf-8 -*-
import os
from alshain import utils


def main(argv):
    altair_path = utils.AltairPath()

    home_dir = os.environ['HOME']

    cartbot_script = altair_path.bin_('altair_cartbot')
    conf = os.path.join(home_dir, '.cartbot.ini')

    cmd = '{} -c {} {} -s 1 -n 1 -C 1 -r 1'.format(cartbot_script, conf, ' '.join(argv))
    return utils.Shell.system(cmd)
