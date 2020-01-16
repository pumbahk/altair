# -*- coding:utf-8 -*-

""" オーソリキャンセルバッチ

"""

import argparse
import logging
from datetime import datetime, timedelta

from pyramid.paster import bootstrap, setup_logging
import sqlahelper
from sqlalchemy.sql import or_
from altair.multicheckout import models as m
from altair.multicheckout.api import get_multicheckout_3d_api, get_all_multicheckout_settings, get_order_no_decorator
from altair.timeparse import parse_time_spec

logger = logging.getLogger(__name__)


def main():
    """
    """
    print "init"


if __name__ == '__main__':
    main()
