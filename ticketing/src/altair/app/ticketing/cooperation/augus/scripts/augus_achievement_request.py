#! /usr/bin/env python
#-*- coding: utf-8 -*-
import logging
import argparse
from pyramid.paster import (
    bootstrap,
    setup_logging,
    )
from altair import multilock
from altair.app.ticketing.core.models import (
    Mailer,
    AugusPerformance,
    )
from ..operations import AugusOperationManager
from ..config import get_var_dir


logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    setup_logging(args.conf)
    env = bootstrap(args.conf)
    settings = env['registry'].settings
    var_dir = get_var_dir(settings)
    mailer = Mailer(settings)
    mgr = AugusOperationManager(var_dir=var_dir)
    try:
        with multilock.MultiStartLock('augus_achievement_request'):
            mgr.achieve_request(mailer)
    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))
        return

if __name__ == '__main__':
    main()
