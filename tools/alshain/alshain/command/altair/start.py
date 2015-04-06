# -*- coding: utf-8 -*-
from ... import utils


def main(argv):
    utils.Shell.system('alshain middleware start')
    utils.Shell.system('alshain daemon start')
    utils.Shell.system('alshain ctl start all')
