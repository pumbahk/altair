# -*- coding: utf-8 -*-
from .. import utils


def main(argv):
    altair_path = utils.AltairPath()
    cmd = altair_path.bin_('supervisorctl')
    line = '{} {}'.format(cmd, ' '.join(argv))
    return utils.Shell.system(line, sudo=True)
