#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import argparse
import urlparse
from altair.augus.transporters import FTPTransporter
from altair.augus.parsers import AugusParser

from ..utils import (
    get_argument_parser,
    get_settings,
    mkdir_p,
    )

def main():
    parser = get_argument_parser()
    args = parser.parse_args()
    settings = get_settings(args.conf)

    staging = settings['staging']
    mkdir_p(staging)

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
