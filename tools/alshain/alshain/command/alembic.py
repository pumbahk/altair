# -*- coding: utf-8 -*-
import os
import jumon
from .. import utils


TARGET_CURRENTDIR = {'ticketing': 'ticketing',
                     'cms': 'cms',
                     }


def get_alembic(target):
    altair_path = utils.AltairPath()
    cmd = altair_path.bin_('altair_alembic_paste')
    conf_file = altair_path.conf('altair.{}.admin.ini'.format(target))
    cmd += ' -c {} '.format(conf_file)
    return cmd


def clean_alembic(target):
    altair_path = utils.AltairPath()
    cur = altair_path.root(target)
    utils.Shell.system('rm -f {}/alembic/versions/*.pyc'.format(cur), sudo=True)
    utils.Shell.system('rm -f {}/alembic/versions/*~'.format(cur), sudo=True)


def main(argv):
    parser = jumon.TransparentOptionParser()
    opts, args = parser.parse_args(argv)

    try:
        target = args[0]
        alembic_args = args[1:]
    except IndexError:
        parser.error()

    altair_path = utils.AltairPath()
    cur = altair_path.root(target)
    os.chdir(cur)
    clean_alembic(cur)
    alembic = get_alembic(target)
    cmd = alembic + ' ' + ' '.join(alembic_args)
    return utils.Shell.system(cmd, sudo=True)
