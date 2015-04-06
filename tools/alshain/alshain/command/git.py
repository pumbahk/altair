# -*- coding: utf-8 -*-
import os
from .. import utils


def main(argv):
    altair_path = utils.AltairPath()
    src_root = altair_path.root()
    os.chdir(src_root)
    cmd = 'git {}'.format(' '.join(argv))
    return utils.Shell.system(cmd, sudo=True)
