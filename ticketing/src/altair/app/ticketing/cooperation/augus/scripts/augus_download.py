#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import logging
import argparse
import urlparse
from altair.app.ticketing.core.models import OrganizationSetting
from altair.augus.transporters import FTPTransporter
from altair.augus.parsers import AugusParser
from altair import multilock
from pyramid.paster import (
    bootstrap,
    setup_logging,
    )

logger = logging.getLogger(__name__)

def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

import os
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
    )
from pyramid.decorator import reify
from altair.augus.transporters import FTPTransporter
from altair.augus.parsers import AugusParser
from altair.app.ticketing.core.models import (
    AugusAccount,
    )
from ..config import get_var_dir
from ..operations import (
    AugusOperationManager,
    )

class AugusAccountNotFound(Exception):
    pass



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    setup_logging(args.conf)
    env = bootstrap(args.conf)
    settings = env['registry'].settings
    var_dir = get_var_dir(settings)

    mgr = AugusOperationManager(var_dir=var_dir)
    try:
        with multilock.MultiStartLock('augus_download'):
            mgr.download()
    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))


if __name__ == '__main__':
    main()
