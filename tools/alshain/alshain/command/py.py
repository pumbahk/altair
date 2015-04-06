# -*- coding: utf-8 -*-
import os
import jumon
from .. import utils


def main(argv):
    cur = utils.DeploySwitcher.get_dir()
    altairpy = os.path.join(cur, 'bin', 'altairpy')
    cmd = altairpy + ' ' + jumon.escape_join(argv)
    child = jumon.call(cmd)
    return child.wait()
