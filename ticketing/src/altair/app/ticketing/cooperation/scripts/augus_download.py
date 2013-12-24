#! /usr/bin/env python
#-*- coding: utf-8 -*-
import os
import argparse
import urlparse
from altair.augus.transporters import FTPTransporter
from altair.augus.parsers import AugusParser

def get_settings(conf=None):
    if conf:
        raise NotImplementedError()
    else:
        from pit import Pit
        return Pit.get('augus_ftp',
                       {'require': {'url': '',
                                    'username': '',
                                    'password': '',
                                    'local': '',
                                    }})

def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', default=None)
    args = parser.parse_args()
    settings = get_settings(args.conf)

    local = settings['local']
    mkdir_p(local)

    url = urlparse.urlparse(settings['url'])
    transporter = FTPTransporter(hostname=url.netloc,
                                 username=settings['username'],
                                 password=settings['password'],
                                 )
    transporter.chdir(url.path)
    for name in transporter.listdir():
        if AugusParser.is_protocol(name):
            transporter.get(name, os.path.join(local, name), remove=True)

if __name__ == '__main__':
    main()
