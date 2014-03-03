#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import shutil
import logging
import argparse
import urlparse
from altair.app.ticketing.core.models import OrganizationSetting
from altair.augus.transporters import FTPTransporter
from altair.augus.parsers import AugusParser
from pyramid.paster import bootstrap
from .. import multilock

logger = logging.getLogger(__name__)

def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def upload_all(settings):
    ko_staging = settings['ko_staging']
    ko_pending = settings['ko_pending']

    mkdir_p(ko_staging)
    mkdir_p(ko_pending)

    org_settings = OrganizationSetting.query.filter(
        OrganizationSetting.augus_use==True).all()

    for org_setting in org_settings:
        if org_setting.organization_id != 15:# RT only
            continue
        url = urlparse.urlparse(org_setting.augus_upload_url)
        transporter = FTPTransporter(hostname=url.netloc,
                                     username=org_setting.augus_username,
                                     password=org_setting.augus_password,
                                     )
        logger.info('ftp chdir: {}'.format(url.path))
        transporter.chdir(url.path)
        for name in os.listdir(ko_staging):
            if AugusParser.is_protocol(name):
                src = os.path.join(ko_staging, name)
                dst = name
                pending_dst = os.path.join(ko_pending, name)
                logger.info('augus file upload: {} -> {}'.format(src, dst))
                transporter.put(src, dst)
                shutil.move(src, pending_dst)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    env = bootstrap(args.conf)
    settings = env['registry'].settings


    try:
        with multilock.MultiStartLock('augus_upload'):
            upload_all(settings)
    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))


if __name__ == '__main__':
    main()
