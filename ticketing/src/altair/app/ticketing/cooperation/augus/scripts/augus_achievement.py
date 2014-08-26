#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import time
import logging
import argparse
from pyramid.renderers import render_to_response
from pyramid.paster import (
    bootstrap,
    setup_logging,
    )
import transaction
from altair.augus.exporters import AugusExporter
from altair.augus.parsers import AugusParser
from altair.augus.protocols import AchievementRequest
from altair import multilock
from altair.app.ticketing.core.models import (
    Mailer,
    AugusPerformance,
    )
from ..operations import AugusOperationManager
from ..exporters import AugusAchievementExporter
from ..config import get_var_dir
from ..errors import (
    IllegalImportDataError,
    AugusDataImportError,
    )


logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    parser.add_argument('--force', action='store_true', default=False)
    args = parser.parse_args()
    setup_logging(args.conf)
    env = bootstrap(args.conf)
    settings = env['registry'].settings
    mailer = Mailer(settings)

    var_dir = get_var_dir(settings)
    mailer = Mailer(settings)

    mgr = AugusOperationManager(var_dir=var_dir)
    try:
        with multilock.MultiStartLock('augus_achievement'):
            mgr.achieve(mailer, args.force)
    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))
        return

if __name__ == '__main__':
    main()
