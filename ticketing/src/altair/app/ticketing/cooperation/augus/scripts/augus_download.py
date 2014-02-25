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

logger = logging.getLogger(__name__)

def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def download_all(settings):
    rt_staging = settings['rt_staging']

    mkdir_p(rt_staging)

    org_settings = OrganizationSetting.query.filter(
        OrganizationSetting.augus_use==True).all()
    for org_setting in org_settings:
        if org_setting.organization_id != 15:# RT only
            continue
        url = urlparse.urlparse(org_setting.augus_download_url)
        transporter = FTPTransporter(hostname=url.netloc,
                                     username=org_setting.augus_username,
                                     password=org_setting.augus_password,
                                     )
        transporter.chdir(url.path)
        for name in transporter.listdir():
            if AugusParser.is_protocol(name):
                src = name
                dst = os.path.join(rt_staging, name)
                logger.info('augus file download: {} -> {}'.format(src, dst))
                transporter.get(src, dst, remove=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    env = bootstrap(args.conf)
    settings = env['registry'].settings

    try:
        with multilock.MultiStartLock('augus_download'):
            download_all(settings)
    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))




if __name__ == '__main__':
    main()
