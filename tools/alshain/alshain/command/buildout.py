# -*- coding: utf-8 -*-
import os
from .. import utils


def main(argv):
    cfg_name = ''
    if len(argv):
        cfg_name = argv[0]
    altair_path = utils.AltairPath()
    cur = altair_path.style()
    os.chdir(cur)
    style = altair_path.get_style()
    if style in (utils.DeployStyle.develop.value, utils.DeployStyle.staging.value):
        utils.Shell.system('rm -rf conf/altair.*.ini', sudo=True)
    utils.Shell.system('virtualenv env --no-site-packages', sudo=True)
    utils.Shell.system('env/bin/pip install setuptools -U', sudo=True)
    utils.Shell.system('touch buildout.cfg', sudo=True)
    utils.Shell.system('env/bin/python bootstrap.py', sudo=True)
    buildout = altair_path.style('./buildout.sh {}'.format(cfg_name))
    if utils.DeployStyle.develop.value == style:
        buildout = altair_path.bin_('buildout') + ' -c buildout.local.cfg'
    return utils.Shell.system(buildout, sudo=True)
