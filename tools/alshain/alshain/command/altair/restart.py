# -*- coding: utf-8 -*-
from ... import utils


def main(argv):
    utils.Shell.system('alshain altair stop')
    utils.Shell.system('alshain altair start')
