#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import shutil
import logging
import argparse
from altair.app.ticketing.core.models import OrganizationSetting
from altair.augus.transporters import FTPTransporter
from altair.augus.parsers import AugusParser
from pyramid.paster import bootstrap

logger = logging.getLogger(__name__)

def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('conf', nargs='?', default=None)
    args = parser.parse_args()
    env = bootstrap(args.conf)
    settings = env['registry'].settings

    rt_staging = settings['rt_staging']
    rt_pending = settings['rt_pending']
    ko_staging = settings['ko_staging']

    mkdir_p(rt_staging)
    mkdir_p(rt_pending)


    url = urlparse.urlparse(settings['url'])
    transporter = FTPTransporter(hostname=url.netloc,
                                 username=settings['username'],
                                 password=settings['password'],
                                 )
    transporter.chdir(url.path)
    for name in transporter.listdir():
        if AugusParser.is_protocol(name):
            transporter.get(name, os.path.join(staging, name), remove=True)

if __name__ == '__main__':
    main()
