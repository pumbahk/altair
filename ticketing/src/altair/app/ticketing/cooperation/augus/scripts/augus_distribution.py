#! /usr/bin/env python
#-*- coding: utf-8 -*-
import sys
import os
import time
import traceback
import shutil
import logging
import argparse
from pyramid.renderers import render_to_response
from altair.app.ticketing.core.models import (
    Mailer,
    AugusPerformance,
    AugusStockDetail,
    )
from altair.augus.types import Status
from altair.augus.exporters import AugusExporter
from altair.augus.protocols import (
    DistributionSyncRequest,
    DistributionSyncResponse,
    )
from altair.augus.parsers import AugusParser
from altair import multilock
from pyramid.paster import (
    bootstrap,
    setup_logging,
    )
import transaction
from ..importers import AugusDistributionImporter
from ..exporters import AugusDistributionExporter
from ..mails import AugusDistributionMialer
from ..operations import AugusOperationManager
from ..config import get_var_dir
from ..errors import (
    IllegalImportDataError,
    AugusDataImportError,
    )

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    setup_logging(args.conf)
    env = bootstrap(args.conf)
    settings = env['registry'].settings
    var_dir = get_var_dir(settings)
    mailer = AugusDistributionMialer(settings)

    mgr = AugusOperationManager(var_dir=var_dir)
    try:
        with multilock.MultiStartLock('augus_distribution'):
            mgr.distribute(mailer)
    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))

if __name__ == '__main__':
    main()
