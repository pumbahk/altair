# -*- coding: utf-8 -*-
from ... import utils


def main(argv):
    utils.Shell.system('alshain ctl stop all')
    utils.Shell.system('alshain daemon stop')
    utils.Shell.system('alshain middleware stop')
